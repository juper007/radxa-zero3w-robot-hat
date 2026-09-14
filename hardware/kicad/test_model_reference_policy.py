"""Prevent unrelated host/socket geometry from returning to the Radxa HAT."""
from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parent
J4_LIBRARY = ROOT / 'Library_Pollen.pretty/PinHeader_2x20_P2.54mm_Vertical_with_rasp_HAT_zero_SMD_connector.kicad_mod'
J4_MODEL = ROOT / 'models-local/REF-182665-01.step'


class ModelReferencePolicy(unittest.TestCase):
    def test_exact_j4_model_reference_and_placement(self):
        for path in (ROOT / 'radxa_zero3w_robot_hat.kicad_pcb', J4_LIBRARY):
            text = path.read_text(encoding='utf-8')
            for marker in ('(model "${KIPRJMOD}/models-local/REF-182665-01.step"',
                           '(xyz 0 -4.19905533063427 0.302503373819)'):
                with self.subTest(file=path.name, marker=marker):
                    self.assertEqual(text.count(marker), 1)

    @unittest.skipUnless(J4_MODEL.exists(), 'Licensed local STEP absent; render is incomplete')
    def test_installed_local_j4_model_hash(self):
        self.assertEqual(hashlib.sha256(J4_MODEL.read_bytes()).hexdigest(),
                         'd5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5')

    def test_unrelated_host_and_socket_models_are_absent(self):
        for path in (ROOT / 'radxa_zero3w_robot_hat.kicad_pcb', J4_LIBRARY):
            text = path.read_text(encoding='utf-8')
            for forbidden in ('rasp_pi_zero_2_W_with_40_pin_male_connector', 'HDR-SMD_40P-P2.54-V-F-R2-C20-S6.6_FH-00339'):
                with self.subTest(file=path.name, model=forbidden):
                    self.assertEqual(text.count(forbidden), 0, 'Unrelated model cannot be used as exact Radxa/J4 mechanical evidence')


if __name__ == '__main__':
    unittest.main(verbosity=2)
