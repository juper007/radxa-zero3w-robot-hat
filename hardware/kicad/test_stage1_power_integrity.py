"""Stage 1 native acceptance probes; RED on the pre-correction design.
Run with KiCad 10.0.6 bundled Python after native XML regeneration.
These are not replacement guards and do not authorize geometry/hash exceptions.
"""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parent
NETLIST = ROOT.parents[1] / 'validation/strict_port/radxa_port_netlist.xml'

class Stage1Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = ET.parse(NETLIST).getroot()
        cls.parts = {c.get('ref'): c for c in cls.xml.findall('./components/comp')}
        cls.board = pcbnew.LoadBoard(str(ROOT / 'radxa_zero3w_robot_hat.kicad_pcb'))
        cls.footprints = {f.GetReference(): f for f in cls.board.GetFootprints()}
        cls.nets = {(n.get('ref'), n.get('pin')): net.get('name')
                    for net in cls.xml.findall('./nets/net') for n in net.findall('node')}

    def test_q2_exact_identity(self):
        self.assertEqual(self.parts['Q2'].findtext('value'), 'DMN3023L-7', 'Q2 gate-rated replacement missing')
        self.assertEqual(self.footprints['Q2'].GetValue(), 'DMN3023L-7')
        fields = {f.get('name'): f.text or '' for f in self.parts['Q2'].findall('./fields/field')}
        self.assertEqual(fields.get('Manufacturer_Part_Number'), 'DMN3023L-7')
        self.assertEqual(fields.get('Manufacturer_Name'), 'Diodes Incorporated')
        self.assertNotEqual(fields.get('LCSC Part'), 'C142518', 'old Si2312 purchasing identity remains')

    def test_q2_enhancement_symbol(self):
        self.assertNotIn('Depletion', self.parts['Q2'].find('libsource').get('part'))
        self.assertIn('enhancement', self.parts['Q2'].findtext('description').lower())

    def test_r8_battery_bias_both_native_sources(self):
        self.assertEqual(self.nets[('R8', '1')], '+BATT', 'R8.1 still uses post-Q2 +5V')
        self.assertEqual(next(p for p in self.footprints['R8'].Pads() if p.GetNumber() == '1').GetNetname(), '+BATT')
        self.assertEqual(self.nets[('R8', '2')], self.nets[('U10', '1')])
        self.assertEqual(self.nets[('C39', '1')], self.nets[('U10', '1')])
        self.assertEqual(self.nets[('C39', '2')], 'GND')

    def test_c39_exact_manufacturer_verified_50v_identity(self):
        fields = {f.get('name'): f.text or '' for f in self.parts['C39'].findall('./fields/field')}
        self.assertEqual(fields.get('Manufacturer_Part_Number'), 'CL05B104KB5NNNC', 'C39 exact 50V purchasing identity missing')
        self.assertEqual(fields.get('Manufacturer_Name'), 'Samsung Electro-Mechanics')
        self.assertEqual(self.parts['C39'].findtext('value'), '100nF 50V X7R')
        self.assertEqual(self.footprints['C39'].GetValue(), '100nF 50V X7R')
        self.assertEqual(self.parts['C39'].findtext('footprint'), 'Capacitor_SMD:C_0402_1005Metric')
        self.assertNotEqual(fields.get('LCSC Part'), 'C1525', 'C1525 is 16V CL05B104KO5NNNC, not this 50V MPN')

    def test_control_preserved_power_pin_directions(self):
        for pin, name in [('1', 'Net-(Q2-G)'), ('2', 'Net-(D1-K)'), ('3', '+5V')]:
            self.assertEqual(self.nets[('Q2', pin)], name)
            self.assertEqual(next(p for p in self.footprints['Q2'].Pads() if p.GetNumber() == pin).GetNetname(), name)
        self.assertEqual(self.nets[('U10', '4')], self.nets[('Q2', '2')])
        self.assertEqual(self.nets[('U10', '5')], self.nets[('Q2', '1')])
        self.assertEqual(self.nets[('U10', '6')], self.nets[('Q2', '3')])

if __name__ == '__main__':
    unittest.main(verbosity=2)
