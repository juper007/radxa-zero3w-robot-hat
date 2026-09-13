"""Stage 2 semantic mutations of fresh native XML and merged schematics."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_stage1_guards import helpers, ROOT

REFS = ('Q3', 'Q4', 'Q5', 'R24', 'R3', 'R42', 'R43', 'R44', 'R45', 'R46')

class Stage2Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = helpers()
        cls.tmp = tempfile.TemporaryDirectory(prefix='stage2-guard-tests-')
        cls.net = Path(cls.tmp.name) / 'fresh.xml'
        cli = cls.ns['find_kicad_cli']()
        cls.ns['require_kicad_version'](cli)
        cls.ns['run_kicad'](cli, ['sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(cls.net), str(cls.ns['SCH'])])
        cls.sheets = {name: (ROOT / (name + '.kicad_sch')).read_text(encoding='utf-8') for name in ('power', 'audio', 'main')}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, tree=None):
        self.assertIn('validate_stage2_netlist', self.ns, 'Stage 2 semantic guard missing')
        path = self.net
        if tree is not None:
            path = Path(self.tmp.name) / 'mutation.xml'
            tree.write(path, encoding='utf-8')
        self.ns['validate_stage2_netlist'](path)

    def test_fresh_candidate(self):
        self.check()

    def test_reject_raw_battery_tied_amp_wrong_gpio_and_bias(self):
        for ref, pin, destination in [('R24','1','/Schematic/Audio/GPIO3_B4_P31'), ('U1','12','+5V'), ('J4','11','GND'), ('R46','2','+5V'), ('R43','2','+BATT'), ('Q4','2','+5V')]:
            tree = ET.parse(self.net)
            nets = {n.get('name'): n for n in tree.findall('./nets/net')}
            source = next(n for n in nets.values() if n.find(f"node[@ref='{ref}'][@pin='{pin}']") is not None)
            node = source.find(f"node[@ref='{ref}'][@pin='{pin}']")
            source.remove(node)
            nets[destination].append(node)
            with self.subTest(ref=ref, pin=pin), self.assertRaisesRegex(SystemExit, 'Stage 2'):
                self.check(tree)

    def test_reject_netlist_part_identity_population_and_presence(self):
        for ref in REFS:
            for field in ('value', 'footprint', 'Manufacturer_Name', 'Manufacturer_Part_Number', 'dnp', 'missing'):
                tree = ET.parse(self.net)
                comp = tree.find(f"./components/comp[@ref='{ref}']")
                if field == 'missing':
                    tree.find('./components').remove(comp)
                elif field == 'dnp':
                    ET.SubElement(comp, 'property', name='dnp')
                elif field in ('value', 'footprint'):
                    comp.find(field).text = 'WRONG'
                else:
                    comp.find(f"./fields/field[@name='{field}']").text = 'WRONG'
                with self.subTest(ref=ref, field=field), self.assertRaisesRegex(SystemExit, ref):
                    self.check(tree)

    def test_schematic_population_identity_presence(self):
        self.assertTrue('validate_stage2_schematics' in self.ns, 'Stage 2 schematic guard missing')
        check = self.ns['validate_stage2_schematics']
        check(self.sheets)
        for ref in REFS:
            sheet = 'power' if ref in ('Q3', 'R24', 'R42', 'R43') else 'audio'
            block = self.ns['symbol_block'](self.sheets[sheet], ref)
            mutations = [block.replace('(dnp no)', '(dnp yes)'), block.replace('(in_bom yes)', '(in_bom no)'), block.replace('(on_board yes)', '(on_board no)'), '']
            for key in ('Value', 'Footprint', 'Manufacturer_Name', 'Manufacturer_Part_Number'):
                value = self.ns['property_value'](block, key)
                mutations.append(block.replace(f'(property "{key}" "{value}"', f'(property "{key}" "WRONG"', 1))
            if ref.startswith('Q'):
                mutations.append(block.replace('Transistor_BJT:Q_NPN_BEC', 'Transistor_BJT:Q_PNP_BEC'))
            for mutation in mutations:
                changed = dict(self.sheets)
                changed[sheet] = changed[sheet].replace(block, mutation, 1)
                with self.subTest(ref=ref, mutation=mutation[:30]), self.assertRaisesRegex(SystemExit, ref):
                    check(changed)

    def test_precise_upstream_normalization(self):
        self.ns['validate_upstream_netlist'](self.ns['BASE_NETLIST'], self.net)
        for ref, pin in [('R4','1'), ('R8','1'), ('J4','13'), ('R43','2')]:
            tree = ET.parse(self.net)
            node = tree.find(f"./nets/net/node[@ref='{ref}'][@pin='{pin}']")
            node.set('pintype', 'WRONG')
            path = Path(self.tmp.name) / 'drift.xml'
            tree.write(path, encoding='utf-8')
            with self.subTest(ref=ref), self.assertRaises(SystemExit):
                self.ns['validate_upstream_netlist'](self.ns['BASE_NETLIST'], path)

    def test_production_wiring_and_pin11_header_contract(self):
        import ast
        tree = ast.parse((ROOT / 'check_strict_port.py').read_text(encoding='utf-8'))
        calls = [n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertIn('validate_stage2_schematics', calls)
        self.assertIn('validate_stage2_pcb', calls)
        headers = [ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'expected_header' for t in n.targets)]
        self.assertEqual(headers[0][11], 'AMP_ENABLE')
        self.assertEqual({pin for pin, net in headers[0].items() if net.startswith('unconnected-')}, {13, 16, 18, 22, 26, 32, 33, 36, 37})

    def test_pcb_population_identity_fixture(self):
        # Explicit unit fixture: NOT routed PCB evidence. Actual merged-board
        # population and identity mutations are exercised separately below.
        self.assertTrue('validate_stage2_pcb' in self.ns, 'Stage 2 PCB guard missing')
        check = self.ns['validate_stage2_pcb']
        blocks = {}
        for ref, identity in self.ns['stage2_identities']().items():
            props = '\n'.join(f'\t\t(property "{key}" "{value}")' for key, value in {'Reference': ref, **identity}.items())
            blocks[ref] = f'\n\t(footprint "{identity["Footprint"]}"\n{props}\n\t\t(attr smd)\n\t)'
        fixture = '(kicad_pcb' + ''.join(blocks.values()) + '\n)'
        check(fixture)
        for ref, block in blocks.items():
            mutations = ['', block.replace('(attr smd)', '(attr smd dnp)'), block.replace('(attr smd)', '(attr smd exclude_from_bom)'), block.replace('(attr smd)', '(attr smd exclude_from_pos_files)')]
            for key, value in self.ns['stage2_identities']()[ref].items():
                mutations.append(block.replace(f'"{value}"', '"WRONG"', 1))
            for mutation in mutations:
                with self.subTest(ref=ref), self.assertRaisesRegex(SystemExit, ref):
                    check(fixture.replace(block, mutation, 1))

    def test_reject_d2_restoration_duplicate_records_and_wrong_transistor_symbol(self):
        import copy
        for mutation in ('D2', 'duplicate_component', 'duplicate_net', 'PNP'):
            tree = ET.parse(self.net)
            if mutation == 'D2':
                old = ET.parse(self.ns['BASE_NETLIST']).find("./components/comp[@ref='D2']")
                tree.find('./components').append(old)
            elif mutation == 'duplicate_component':
                tree.find('./components').append(copy.deepcopy(tree.find("./components/comp[@ref='Q3']")))
            elif mutation == 'duplicate_net':
                tree.find('./nets').append(copy.deepcopy(tree.find("./nets/net[@name='BAT_BASE']")))
            else:
                tree.find("./components/comp[@ref='Q3']/libsource").set('part', 'Q_PNP_BEC')
            with self.subTest(mutation=mutation), self.assertRaisesRegex(SystemExit, 'Stage 2'):
                self.check(tree)

    def test_exact_stage2_parity_resolution_set(self):
        import copy
        self.assertTrue('stage2_resolved_parity' in self.ns, 'exact parity-resolution guard missing')
        rows = self.ns['load_json'](self.ns['BASE_DRC'])['schematic_parity']
        selected = self.ns['stage2_resolved_parity'](rows)
        self.assertEqual(len(selected), 3)
        for row in selected:
            for mutation in ('omit', 'severity', 'duplicate'):
                changed = copy.deepcopy(rows)
                index = rows.index(row)
                if mutation == 'omit':
                    changed.pop(index)
                elif mutation == 'duplicate':
                    changed.append(copy.deepcopy(row))
                else:
                    changed[index]['severity'] = 'error'
                with self.subTest(mutation=mutation), self.assertRaisesRegex(SystemExit, 'Stage 2'):
                    self.ns['stage2_resolved_parity'](changed)

    def test_merged_pcb_population_and_identity(self):
        pcb = self.ns['PCB'].read_text(encoding='utf-8')
        check = self.ns['validate_stage2_pcb']
        check(pcb)
        for ref in REFS:
            block = self.ns['footprint_block'](pcb, ref)
            for changed in ('', block.replace('(attr smd)', '(attr smd dnp)', 1)):
                with self.subTest(ref=ref), self.assertRaisesRegex(SystemExit, ref):
                    check(pcb.replace(block, changed, 1))
            for key in ('Value', 'Manufacturer_Name', 'Manufacturer_Part_Number'):
                value = self.ns['property_value'](block, key)
                changed = block.replace(f'(property "{key}" "{value}"', f'(property "{key}" "WRONG"', 1)
                with self.subTest(ref=ref, key=key), self.assertRaisesRegex(SystemExit, ref):
                    check(pcb.replace(block, changed, 1))

if __name__ == '__main__':
    unittest.main(verbosity=2)
