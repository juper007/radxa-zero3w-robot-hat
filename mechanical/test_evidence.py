"""Offline synthetic evidence regressions: Python + Pillow, no KiCad/CAD/models.
Public JSON supplies the geometric schema; every input file and PNG is synthetic.
Only official asset pins are substituted in the isolated verifier process, so
integrity checks exercise real bytes without redistributing licensed CAD files.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='radxa-evidence-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / 'mechanical'
        self.evidence.mkdir()
        self.scratch = self.root / 'scratch'
        self.scratch.mkdir()
        for p in ROOT.glob('*.py'):
            shutil.copy2(p, self.evidence / p.name)
        for name in ['cad_evidence.json','j4_evidence.json','render_evidence.json']:
            shutil.copy2(ROOT/name, self.evidence/name)
        c = json.loads((self.evidence/'cad_evidence.json').read_text())
        i = c['inputs']
        pcb = self.root/'fixture.kicad_pcb'
        pcb.write_bytes(b'synthetic source PCB; not a CAD model')
        i.update(source_pcb=str(pcb), pcb_sha256=sha(pcb), cache_sha256=None, cache_matches_current=False)
        for name in ['official-current.zip','official_radxa.stp','c45.step','board.step','surfaces.step','bottom.step','j4-current.step']:
            (self.scratch/name).write_bytes(('synthetic '+name).encode())
        i.update(zip_sha256=sha(self.scratch/'official-current.zip'), step_sha256=sha(self.scratch/'official_radxa.stp'))
        row = c['placements']['header_grid_aligned']
        tx, ty, _ = row['native_kicad_step_to_radxa_translation_mm']
        close = sorted(row['bottom_solids_under_1mm'], key=lambda b: b['minimum_distance_mm'])
        i['footprints'] = []
        for n in range(73):
            bb = close[n]['bbox_mm'] if n < len(close) else [0,0,0,0]
            i['footprints'].append(dict(ref='C7' if n == 0 else ('J4' if n == 12 else 'FIX'+str(n)), layer='B.Cu', dnp=n>=67, x_mm=(bb[0]+bb[1])/2-tx, y_mm=ty-(bb[2]+bb[3])/2, models=[dict(path='${KIPRJMOD}/models-local/REF-182665-01.step', rotation=[-90,0,90])]))
        for name, row in c['exports'].items():
            row['sha256'] = sha(self.scratch/name)
        self.save('cad_evidence.json', c)
        self.save('inputs.json', i, scratch=True)
        j = json.loads((self.evidence/'j4_evidence.json').read_text())
        j.update(source_pcb_sha256=sha(pcb), analyzed_native_step=str(self.scratch/'j4-current.step'), analyzed_native_step_sha256=sha(self.scratch/'j4-current.step'))
        model = self.root/'licensed-fixture.step'
        model.write_bytes(b'synthetic connector, not licensed CAD')
        binding = dict(source_pcb=str(pcb), source_pcb_sha256=sha(pcb), model_file=str(model), model_sha256=sha(model), native_step_file='j4-current.step', native_step_sha256=sha(self.scratch/'j4-current.step'), source_unchanged=True, rotation_deg=[-90,0,90], offset_mm=[0,-4.19905533063427,.302503373819], scale=[1,1,1])
        j.update(binding)
        self.save('j4-current-metadata.json', binding, scratch=True)
        self.save('j4_evidence.json', j)
        v = json.loads((self.evidence/'render_evidence.json').read_text())
        for row in v['sources']:
            row['sha256'] = sha(self.scratch/row['file'])
        v['outputs'] = []
        for name in ['stack_4mm.png','stack_4mm_header_side.png']:
            # Uncompressed PNG also meets the legacy size-only check.
            Image.new('RGB',(1600,1000),(70,80,90)).save(self.evidence/name, compress_level=0)
            v['outputs'].append(dict(file=name, sha256=sha(self.evidence/name), bytes=(self.evidence/name).stat().st_size))
        self.save('render_evidence.json', v)
        self.pins = dict(OFFICIAL_ZIP_SHA256=i['zip_sha256'], OFFICIAL_STEP_SHA256=i['step_sha256'], J4_MODEL_SHA256=sha(model))

    def save(self, name, data, scratch=False):
        ((self.scratch if scratch else self.evidence)/name).write_text(json.dumps(data))

    def mutate(self, name, change, scratch=False):
        p = (self.scratch if scratch else self.evidence) / name
        data = json.loads(p.read_text())
        change(data)
        p.write_text(json.dumps(data))

    def verify(self, optimized=False):
        # Isolate pin substitution to synthetic tests, never production CLI flags.
        bootstrap = ('import sys,runpy,importlib.util;sys.path.insert(0,'+repr(str(self.evidence))+');'
                     'spec=importlib.util.find_spec("evidence_contract");'
                     'm=__import__("evidence_contract") if spec else None;'
                     '[setattr(m,k,v) for k,v in '+repr(self.pins)+'.items()] if m else None;'
                     'sys.argv='+repr([str(self.evidence/'verify_evidence.py'),'--scratch',str(self.scratch)])+';'
                     'runpy.run_path(sys.argv[0],run_name="__main__")')
        return subprocess.run([sys.executable, *(['-O'] if optimized else []), '-c', bootstrap], capture_output=True, text=True)

    def reject(self, diagnostic, optimized=False):
        result = self.verify(optimized)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stderr)

    def test_missing_surfaces_export_and_file(self):
        self.mutate('cad_evidence.json', lambda c: c['exports'].pop('surfaces.step'))
        (self.scratch/'surfaces.step').unlink()
        self.reject('CAD export inventory')

    def test_cad_export_inventory(self):
        original = (self.evidence/'cad_evidence.json').read_bytes()
        required = ['official_radxa.stp','c45.step','board.step','bottom.step','surfaces.step']
        for name in required:
            with self.subTest(missing=name):
                (self.evidence/'cad_evidence.json').write_bytes(original)
                self.mutate('cad_evidence.json', lambda c: c['exports'].pop(name))
                path = self.scratch/name
                content = path.read_bytes()
                path.unlink()
                try:
                    self.reject('CAD export inventory')
                finally:
                    path.write_bytes(content)
        for kind in ['missing','empty','unexpected']:
            with self.subTest(kind=kind):
                (self.evidence/'cad_evidence.json').write_bytes(original)
                def change(c):
                    if kind == 'missing': c.pop('exports')
                    elif kind == 'empty': c['exports'] = {}
                    else: c['exports']['unexpected.step'] = c['exports']['surfaces.step'].copy()
                self.mutate('cad_evidence.json', change)
                self.reject('CAD export inventory')

    def test_current_j4_binding(self):
        original = (self.scratch/'j4-current-metadata.json').read_bytes()
        for field in ['source_pcb_sha256','model_sha256','native_step_sha256']:
            with self.subTest(field=field):
                (self.scratch/'j4-current-metadata.json').write_bytes(original)
                self.mutate('j4-current-metadata.json', lambda m: m.update({field:'0'*64}), scratch=True)
                self.reject('J4 binding')

    def test_current_j4_metadata_required(self):
        (self.scratch/'j4-current-metadata.json').unlink()
        self.reject('j4-current-metadata.json')

    def test_j4_evidence_matches_dedicated_export(self):
        self.mutate('j4_evidence.json', lambda j: j.update(native_step_sha256='0'*64))
        self.reject('J4 binding')

    def test_no_historical_cache_required(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['evidence_complete'])

    def test_official_step_bytes_pinned(self):
        (self.scratch/'official_radxa.stp').write_bytes(b'wrong official model')
        # Even self-consistent untrusted metadata must not change the pin.
        digest = sha(self.scratch/'official_radxa.stp')
        self.mutate('inputs.json', lambda i: i.update(step_sha256=digest), scratch=True)
        self.mutate('cad_evidence.json', lambda c: (c['inputs'].update(step_sha256=digest), c['exports']['official_radxa.stp'].update(sha256=digest)))
        self.mutate('render_evidence.json', lambda v: v['sources'][0].update(sha256=digest))
        self.reject('official STEP')

    def test_official_zip_bytes_pinned(self):
        (self.scratch/'official-current.zip').write_bytes(b'wrong archive')
        self.reject('official ZIP')

    def test_optimized_wrong_pcb_rejected(self):
        self.mutate('cad_evidence.json', lambda c: c['inputs'].update(pcb_sha256='0'*64))
        self.reject('optimized', optimized=True)

    def test_render_source_inventory(self):
        original = (self.evidence/'render_evidence.json').read_bytes()
        for kind in ['empty','missing','duplicate','unexpected']:
            with self.subTest(kind=kind):
                (self.evidence/'render_evidence.json').write_bytes(original)
                def change(v):
                    if kind == 'empty': v['sources'] = []
                    elif kind == 'missing': v['sources'].pop()
                    elif kind == 'duplicate': v['sources'].append(v['sources'][0].copy())
                    else: v['sources'][0]['file'] = 'surfaces.step'
                self.mutate('render_evidence.json', change)
                self.reject('render source inventory')

    def test_render_transform(self):
        self.mutate('render_evidence.json', lambda v: v['sources'][1].update(translation_mm=[0,0,0]))
        self.reject('render transform')

    def test_render_source_hash(self):
        self.mutate('render_evidence.json', lambda v: v['sources'][1].update(sha256='0'*64))
        self.reject('render source hash')

    def test_render_output_inventory(self):
        original = (self.evidence/'render_evidence.json').read_bytes()
        for kind in ['empty','missing','duplicate','unexpected']:
            with self.subTest(kind=kind):
                (self.evidence/'render_evidence.json').write_bytes(original)
                def change(v):
                    if kind == 'empty': v['outputs'] = []
                    elif kind == 'missing': v['outputs'].pop()
                    elif kind == 'duplicate': v['outputs'].append(v['outputs'][0].copy())
                    else: v['outputs'][0]['file'] = 'unrelated.png'
                self.mutate('render_evidence.json', change)
                self.reject('render output inventory')

    def test_valid_but_mismatched_png(self):
        Image.new('RGB',(1600,1000),'red').save(self.evidence/'stack_4mm.png', compress_level=0)
        self.reject('render output hash')

    def test_corrupt_png_even_with_matching_output_hash(self):
        p = self.evidence/'stack_4mm.png'
        p.write_bytes(p.read_bytes()[:24]+bytes(11000))
        self.mutate('render_evidence.json', lambda v: v['outputs'][0].update(sha256=sha(p), bytes=p.stat().st_size))
        self.reject('PNG integrity')

    def test_renderer_failed_write_never_binds_stale_png(self):
        import evidence_contract as contract
        publish = getattr(contract, 'publish_render', None)
        self.assertTrue(callable(publish), 'renderer needs checked temporary publication')
        old = (self.evidence/'render_evidence.json').read_bytes()
        metadata = json.loads(old)
        for name in ['no_write','bad_png','second_write_fails']:
            with self.subTest(kind=name):
                def writer(path, view):
                    if name == 'bad_png': path.write_bytes(b'not a PNG')
                    elif name == 'second_write_fails':
                        if view == 1: raise OSError('simulated native write error')
                        Image.new('RGB',(1600,1000),'blue').save(path)
                with self.assertRaises((ValueError, OSError)):
                    publish(self.scratch, self.evidence, metadata, writer)
                self.assertEqual((self.evidence/'render_evidence.json').read_bytes(), old)
                self.assertEqual(sha(self.evidence/'stack_4mm.png'), metadata['outputs'][0]['sha256'])

    def test_renderer_success_binds_new_images(self):
        import evidence_contract as contract
        publish = getattr(contract, 'publish_render', None)
        self.assertTrue(callable(publish), 'renderer needs checked temporary publication')
        metadata = json.loads((self.evidence/'render_evidence.json').read_text())
        def writer(path, view):
            Image.new('RGB',(1600,1000),('blue','red')[view]).save(path)
        publish(self.scratch, self.evidence, metadata, writer)
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)

class AcquisitionTests(unittest.TestCase):
    def test_bounded_pinned_download(self):
        import io
        import zipfile
        from unittest.mock import patch
        import evidence_contract as contract
        acquire = getattr(contract, 'acquire_official', None)
        self.assertTrue(callable(acquire), 'acquisition needs bounded pinned download')
        body = b'synthetic official STEP'
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('host.stp', body)
        archive_bytes = stream.getvalue()
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(contract, 'OFFICIAL_ZIP_SHA256', hashlib.sha256(archive_bytes).hexdigest()), patch.object(contract, 'OFFICIAL_STEP_SHA256', hashlib.sha256(body).hexdigest()):
                with patch('urllib.request.urlopen', return_value=io.BytesIO(archive_bytes)) as request:
                    acquire(out)
                    self.assertEqual((out/'official_radxa.stp').read_bytes(), body)
                    self.assertEqual(request.call_args.kwargs['timeout'], 30)
                before = (out/'official-current.zip').read_bytes()
                with patch('urllib.request.urlopen', return_value=io.BytesIO(b'bad archive')):
                    with self.assertRaisesRegex(ValueError, 'official ZIP'):
                        acquire(out)
                with patch('urllib.request.urlopen', return_value=io.BytesIO(archive_bytes)), patch.object(contract, 'MAX_ARCHIVE_BYTES', 10):
                    with self.assertRaisesRegex(ValueError, 'download size'):
                        acquire(out)
                with patch('urllib.request.urlopen', return_value=io.BytesIO(archive_bytes)), patch.object(contract, 'MAX_STEP_BYTES', 1):
                    with self.assertRaisesRegex(ValueError, 'STEP size'):
                        acquire(out)
                self.assertEqual((out/'official-current.zip').read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
