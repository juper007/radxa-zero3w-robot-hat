"""Pure contracts first; opt-in real CAD exercise via sweep_stack CLI."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).with_name('sweep_stack.py')

class DatumTests(unittest.TestCase):
    def test_measured_datums_at_four_mm(self):
        self.assertTrue(MODULE.exists(), 'missing sweep implementation')
        import sweep_stack as s
        r = s.stack_datums(4.0, -.085, .925, -3.7776, 0., 2.5, 8.5)
        self.assertAlmostEqual(r['translation_z_mm'], 4.085)
        self.assertAlmostEqual(r['socket_lower_face_z_mm'], .3074)
        self.assertAlmostEqual(r['body_lower_face_minus_host_plastic_top_mm'], -2.1926)
        self.assertAlmostEqual(r['pin_tip_above_hat_bottom_mm'], 4.5)
        self.assertAlmostEqual(r['pin_tip_above_hat_top_mm'], 3.49)
        self.assertAlmostEqual(r['axial_entry_past_socket_lower_face_mm'], 8.1926)

    def test_invalid_gap_and_datums_fail_closed(self):
        import sweep_stack as s
        for gap in (0, -1, float('nan'), float('inf')):
            with self.subTest(gap=gap), self.assertRaises(ValueError):
                s.stack_datums(gap, -.085, .925, -3.7776, 0., 2.5, 8.5)
        with self.assertRaises(ValueError):
            s.stack_datums(4, .925, -.085, -3.7776, 0., 2.5, 8.5)

    def test_higher_gaps_clear_lower_body_not_contact_acceptance(self):
        import sweep_stack as s
        for gap in (6.2, 6.5, 7., 8.):
            r = s.stack_datums(gap, -.085, .925, -3.7776, 0., 2.5, 8.5)
            self.assertGreater(r['body_lower_face_minus_host_plastic_top_mm'], 0)
        self.assertAlmostEqual(s.stack_datums(6.2, -.085, .925, -3.7776, 0., 2.5, 8.5)['body_lower_face_minus_host_plastic_top_mm'], .0074)

class BindingTests(unittest.TestCase):
    def test_stale_current_source_rejected_before_exports(self):
        import sweep_stack as s
        import tempfile
        import json
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            evidence = root/'mechanical'; evidence.mkdir()
            scratch = root/'scratch'; scratch.mkdir()
            pcb = root/'hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb'
            pcb.parent.mkdir(parents=True)
            pcb.write_bytes(b'current source differs')
            old = '0'*64
            (scratch/'inputs.json').write_text(json.dumps({'source_pcb': str(pcb), 'pcb_sha256': old}))
            (evidence/'cad_evidence.json').write_text(json.dumps({'inputs': {'pcb_sha256': old}}))
            (evidence/'j4_evidence.json').write_text(json.dumps({'source_pcb_sha256': old}))
            with self.assertRaisesRegex(ValueError, 'current source PCB hash'):
                s.preflight(scratch, evidence)

    def test_inventory_and_hash_mutations_rejected(self):
        import sweep_stack as s
        self.assertTrue(hasattr(s, 'verify_export_inventory'), 'missing fail-closed export check')
        import tempfile
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            records = {}
            for name in s.EXPORT_NAMES:
                (root/name).write_bytes(name.encode())
                records[name] = {'sha256': hashlib.sha256(name.encode()).hexdigest()}
            s.verify_export_inventory(root, records)
            for name in s.EXPORT_NAMES:
                missing = dict(records); missing.pop(name)
                with self.assertRaisesRegex(ValueError, 'inventory'):
                    s.verify_export_inventory(root, missing)
            with self.assertRaisesRegex(ValueError, 'inventory'):
                s.verify_export_inventory(root, dict(records, extra={}))
            (root/'bottom.step').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash'):
                s.verify_export_inventory(root, records)

class PublicationTests(unittest.TestCase):
    def test_complete_payload_published_and_temp_removed(self):
        import json
        import os
        import tempfile
        from unittest.mock import patch
        import sweep_stack as s
        payload = json.dumps({'complete': True, 'rows': list(range(10000))}, indent=2)+'\n'
        real_link = os.link
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'sweep.json'

            def publish(source, destination):
                self.assertFalse(output.exists())
                self.assertEqual(pathlib.Path(source).parent, output.parent)
                self.assertEqual(pathlib.Path(source).read_text(encoding='utf-8'), payload)
                return real_link(source, destination)

            with patch('os.link', side_effect=publish) as link:
                s.publish_evidence(payload, output)
            link.assert_called_once()
            self.assertEqual(output.read_text(encoding='utf-8'), payload)
            self.assertEqual(list(pathlib.Path(td).iterdir()), [output])

    def test_preexisting_target_preserved_and_temp_removed(self):
        import tempfile
        import sweep_stack as s
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'sweep.json'
            output.write_bytes(b'original evidence')
            with self.assertRaises(FileExistsError):
                s.publish_evidence('replacement', output)
            self.assertEqual(output.read_bytes(), b'original evidence')
            self.assertEqual(list(pathlib.Path(td).iterdir()), [output])

    def test_unsupported_links_fail_closed_and_remove_temp(self):
        import errno
        import tempfile
        from unittest.mock import patch
        import sweep_stack as s
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'sweep.json'
            with patch('os.link', side_effect=OSError(errno.ENOTSUP, 'hard links unsupported')):
                with self.assertRaises(OSError) as error:
                    s.publish_evidence('complete payload', output)
            self.assertEqual(error.exception.errno, errno.ENOTSUP)
            self.assertEqual(list(pathlib.Path(td).iterdir()), [])

    def test_flush_failure_never_publishes_and_removes_temp(self):
        import errno
        import tempfile
        from unittest.mock import patch
        import sweep_stack as s
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'sweep.json'
            with patch('os.fsync', side_effect=OSError(errno.EIO, 'flush failed')):
                with self.assertRaises(OSError) as error:
                    s.publish_evidence('complete payload', output)
            self.assertEqual(error.exception.errno, errno.EIO)
            self.assertEqual(list(pathlib.Path(td).iterdir()), [])

    def test_raced_target_is_preserved_at_publication(self):
        import os
        import tempfile
        from unittest.mock import patch
        import sweep_stack as s
        real_link, real_rename = os.link, pathlib.Path.rename
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'sweep.json'

            def race(publish, source, destination):
                self.assertFalse(output.exists())
                output.write_bytes(b'concurrent evidence')
                return publish(source, destination)

            # Interpose only to schedule a real competing write immediately
            # before the real filesystem publication primitive.
            with patch.object(s, 'run_sweep', return_value={'complete': True}), \
                 patch('sys.argv', ['sweep_stack', '--scratch', td, '--output', str(output)]), \
                 patch('os.link', side_effect=lambda a, b: race(real_link, a, b)), \
                 patch.object(pathlib.Path, 'rename', lambda a, b: race(real_rename, a, b)), \
                 patch('os._exit'):
                with self.assertRaises(FileExistsError):
                    s.main()
            self.assertEqual(output.read_bytes(), b'concurrent evidence')
            self.assertEqual(list(pathlib.Path(td).iterdir()), [output])


class RealSweepTests(unittest.TestCase):
    def test_entrypoint_is_import_safe_and_present(self):
        import sys
        import sweep_stack as s
        self.assertNotIn('cadquery', sys.modules)
        self.assertTrue(callable(getattr(s, 'run_sweep', None)), 'missing real CAD sweep')
        self.assertTrue(callable(getattr(s, 'preflight', None)), 'missing source preflight')

    def test_no_overwrite_before_cad_preserves_bytes(self):
        import subprocess
        import tempfile
        import sys
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'existing.json'
            output.write_bytes(b'original evidence')
            result = subprocess.run([sys.executable, str(MODULE), '--scratch',
                str(pathlib.Path(td)/'nonexistent-scratch'), '--output', str(output)],
                capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refusing to overwrite existing evidence', result.stderr)
            self.assertEqual(output.read_bytes(), b'original evidence')
            self.assertNotIn('Preflight passed', result.stdout)

    @unittest.skipUnless(__import__('os').environ.get('RUN_STACK_CAD') == '1', 'opt-in real CAD integration')
    def test_real_cad_sweep(self):
        import subprocess
        import json
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            output = pathlib.Path(td)/'stack_sweep.json'
            result = subprocess.run([sys.executable, str(MODULE), '--scratch',
                'C:/Users/juper/AppData/Local/Temp/radxa-cad-final', '--output', str(output)],
                capture_output=True, text=True, timeout=600)
            print(result.stdout, flush=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists(), 'missing successful sweep artifact')
            report = json.loads(output.read_text())
        self.assertFalse(report['fabrication_ready'])
        self.assertEqual([r['surface_gap_mm'] for r in report['gaps']], [4., 6.2, 6.5, 7., 8., 9., 10.])
        self.assertEqual(report['geometry']['bottom.step']['solids'], 65)
        self.assertEqual(len(report['datums']['host_pin_tip_faces']), 40)
        self.assertGreater(report['gaps'][0]['j4_low_header_region_intersection_mm3'], 400)
        for r in report['gaps'][1:]:
            self.assertLess(r['j4_low_header_region_intersection_mm3'], 1e-8)
        self.assertAlmostEqual(report['gaps'][0]['bottom_to_complete_host']['minimum_distance_mm'], .005, places=6)
        self.assertAlmostEqual(report['gaps'][0]['c45_max_material_envelope_to_host']['minimum_distance_mm'], .465, places=6)

if __name__ == '__main__':
    unittest.main()
