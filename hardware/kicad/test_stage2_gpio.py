"""Exact Stage 2 electrical contract; regenerate the native netlist first."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def pins(root):
    return {(node.get('ref'), node.get('pin')): net.get('name')
            for net in root.findall('./nets/net') for node in net.findall('node')}


class Stage2GPIO(unittest.TestCase):
    def setUp(self):
        self.root = ET.parse(ROOT / 'validation/strict_port/radxa_port_netlist.xml').getroot()
        self.components = {c.get('ref'): c for c in self.root.findall('./components/comp')}
        self.pins = pins(self.root)

    def same(self, *nodes):
        for node in nodes:
            self.assertIn(node, self.pins)
        self.assertEqual(len({self.pins[node] for node in nodes}), 1, nodes)

    def test_exact_parts(self):
        self.assertNotIn('D2', self.components)
        for ref, value in {'Q3':'BC847B', 'Q4':'BC847B', 'Q5':'BC847B',
                           'R24':'100k', 'R42':'100k', 'R46':'100k',
                           'R3':'10k', 'R43':'10k', 'R44':'10k', 'R45':'10k'}.items():
            with self.subTest(ref=ref):
                self.assertIn(ref, self.components)
                c = self.components[ref]
                self.assertEqual(c.findtext('value'), value)
                fields = {f.get('name'):f.text or '' for f in c.findall('./fields/field')}
                mpn = 'BC847B,215' if ref.startswith('Q') else ('RC0402FR-07100KL' if value == '100k' else 'RC0402FR-0710KL')
                self.assertEqual(fields.get('Manufacturer_Part_Number'), mpn)
                self.assertEqual(fields.get('Manufacturer_Name'), 'Nexperia' if ref.startswith('Q') else 'Yageo')

    def test_battery_present_low_host_referenced(self):
        self.same(('R24','1'), ('R42','1'), ('Q3','1'))
        self.same(('Q3','3'), ('R43','1'), ('C44','1'), ('J4','31'))
        self.assertEqual(self.pins[('R24','2')], '+BATT')
        self.assertEqual(self.pins[('R43','2')], '+3V3')
        for node in [('Q3','2'), ('R42','2'), ('C44','2')]:
            self.assertEqual(self.pins[node], 'GND')
        self.assertNotEqual(self.pins[('R24','1')], self.pins[('J4','31')])

    def test_amplifier_default_off_enable(self):
        self.same(('R3','1'), ('Q4','3'), ('U1','12'))
        self.same(('R44','1'), ('Q4','1'), ('Q5','3'))
        self.same(('R45','1'), ('Q5','1'), ('R46','1'))
        self.same(('J4','11'), ('R45','2'))
        self.assertEqual(self.pins[('J4','11')], 'AMP_ENABLE')
        for node in [('R3','2'), ('R44','2'), ('R4','2')]:
            self.assertEqual(self.pins[node], '+5V')
        self.same(('R4','1'), ('U1','5'))
        for node in [('Q4','2'), ('Q5','2'), ('R46','2')]:
            self.assertEqual(self.pins[node], 'GND')

    def test_stage1_not_reverted(self):
        self.assertEqual(self.components['Q2'].findtext('value'), 'DMN3023L-7')
        self.assertEqual(self.components['C39'].findtext('value'), '100nF 50V X7R')
        self.assertEqual(self.pins[('R8','1')], '+BATT')
        self.same(('R8','2'), ('U10','1'), ('C39','1'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
