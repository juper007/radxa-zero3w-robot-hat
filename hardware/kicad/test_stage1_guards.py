"""Stage 1 fail-closed guard mutations, without importing executable checker."""
import ast
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent

def helpers():
    tree=ast.parse((ROOT/'check_strict_port.py').read_text(encoding='utf-8'))
    prefix=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef):break
        if isinstance(node,(ast.Import,ast.ImportFrom,ast.Assign)):prefix.append(node)
    code=ast.Module(body=prefix+[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
    ns={'__file__':str(ROOT/'check_strict_port.py')}
    exec(compile(code,'checker-helpers','exec'),ns)
    return ns

class Stage1GuardMutations(unittest.TestCase):
    def setUp(self):
        self.ns=helpers()
        self.assertIn('validate_stage1_power',self.ns,'Stage 1 exact-identity and bias guard missing')
        self.sch=(ROOT/'power.kicad_sch').read_text(encoding='utf-8')
        self.pcb=(ROOT/'radxa_zero3w_robot_hat.kicad_pcb').read_text(encoding='utf-8')
        self.net=ROOT.parents[1]/'validation/strict_port/radxa_port_netlist.xml'

    def check(self,sch=None,pcb=None,net=None):
        self.ns['validate_stage1_power'](self.sch if sch is None else sch,self.pcb if pcb is None else pcb,self.net if net is None else net)

    def test_qualified_candidate(self):self.check()

    def test_schematic_purchasing_identity_mutations(self):
        for ref in ('Q2','C39'):
            block=self.ns['symbol_block'](self.sch,ref)
            for key in ('Manufacturer_Name','Manufacturer_Part_Number','LCSC Part','Value'):
                value=self.ns['property_value'](block,key)
                changed=block.replace(f'(property "{key}" "{value}"',f'(property "{key}" "UNQUALIFIED"',1)
                with self.subTest(ref=ref,key=key),self.assertRaisesRegex(SystemExit,ref):
                    self.check(sch=self.sch.replace(block,changed,1))

    def test_pcb_identity_and_geometry_mutations(self):
        for ref in ('Q2','C39','R8'):
            block=self.ns['footprint_block'](self.pcb,ref)
            value=self.ns['property_value'](block,'Value')
            changed=block.replace(f'(property "Value" "{value}"','(property "Value" "UNQUALIFIED"',1)
            with self.subTest(ref=ref),self.assertRaisesRegex(SystemExit,ref):
                self.check(pcb=self.pcb.replace(block,changed,1))
        block=self.ns['footprint_block'](self.pcb,'Q2')
        self.assertIn('(size 0.9 0.8)',block)
        with self.assertRaisesRegex(SystemExit,'Q2'):
            self.check(pcb=self.pcb.replace(block,block.replace('(size 0.9 0.8)','(size 1.22 0.65)',1),1))

    def test_battery_envelope_annotation_cannot_claim_5v_input(self):
        self.assertIn('Assumed minimum 6.0V',self.sch)
        with self.assertRaisesRegex(SystemExit,'battery envelope'):
            self.check(sch=self.sch.replace('Assumed minimum 6.0V','Assumed minimum 5.0V',1))

    def test_q2_symbol_regression(self):
        block=self.ns['symbol_block'](self.sch,'Q2')
        with self.assertRaisesRegex(SystemExit,'Q2'):
            self.check(sch=self.sch.replace(block,block.replace('Transistor_FET:Q_NMOS_GSD','Transistor_FET_Other:Q_NMOS_Depletion_GSD'),1))

    def test_native_netlist_identity_and_r8_bias_mutations(self):
        for ref in ('Q2','C39','R8'):
            tree=ET.parse(self.net)
            if ref=='R8':
                nets={n.get('name'):n for n in tree.findall('./nets/net')}
                node=next(n for n in nets['+BATT'].findall('node') if n.get('ref')=='R8' and n.get('pin')=='1')
                nets['+BATT'].remove(node);nets['+5V'].append(node)
            else:
                comp=next(c for c in tree.findall('./components/comp') if c.get('ref')==ref)
                next(f for f in comp.findall('./fields/field') if f.get('name')=='Manufacturer_Part_Number').text='UNQUALIFIED'
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'mutation.xml';tree.write(p,encoding='utf-8')
                with self.subTest(ref=ref),self.assertRaisesRegex(SystemExit,ref):self.check(net=p)

if __name__=='__main__':unittest.main(verbosity=2)
