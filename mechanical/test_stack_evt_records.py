#!/usr/bin/env python
"""Static regression checks for the bounded 9.5 mm/M2 EVT records."""

import csv
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MECHANICAL = ROOT / "mechanical"
AUDIT_PATH = ROOT / "validation" / "strict_port" / "host_pin_reference_audit.json"
CONTINUITY_PATH = MECHANICAL / "STACK_EVT_CONTINUITY.csv"
ISOLATION_PATH = MECHANICAL / "STACK_EVT_ISOLATION.csv"
PLAN_PATH = MECHANICAL / "STACK_EVT_PLAN.md"
SWEEP_PATH = MECHANICAL / "stack_sweep_9p5_evt.json"

CONTINUITY_COLUMNS = {
    "pin",
    "reference_host_identity",
    "hat_net",
    "lead_null_ohm",
    "initial_raw_ohm",
    "initial_corrected_ohm",
    "initial_pass",
    "pressure_raw_ohm",
    "pressure_corrected_ohm",
    "pressure_pass",
    "post_remate_raw_ohm",
    "post_remate_corrected_ohm",
    "post_remate_pass",
    "notes",
}
ISOLATION_COLUMNS = {
    "pair_id",
    "pin_a",
    "pin_a_reference_host_identity",
    "pin_a_hat_net",
    "pin_b",
    "pin_b_reference_host_identity",
    "pin_b_hat_net",
    "relation",
    "lead_null_ohm",
    "premate_j4_toe_raw_ohm",
    "premate_j4_toe_corrected_ohm",
    "premate_pass",
    "initial_raw_ohm",
    "initial_corrected_ohm",
    "initial_pass",
    "pressure_raw_ohm",
    "pressure_corrected_ohm",
    "pressure_pass",
    "post_remate_raw_ohm",
    "post_remate_corrected_ohm",
    "post_remate_pass",
    "notes",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def physical_pairs():
    pairs = []
    pairs.extend((f"cross-row-{(a + 1) // 2:02d}", a, a + 1) for a in range(1, 40, 2))
    pairs.extend((f"odd-column-{(a + 1) // 2:02d}", a, a + 2) for a in range(1, 39, 2))
    pairs.extend((f"even-column-{a // 2:02d}", a, a + 2) for a in range(2, 40, 2))
    return pairs


class StackEvtRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        cls.canonical = {int(row["pin"]): row for row in cls.audit["pins"]}

    def test_continuity_csv_is_exact_canonical_40_pin_record(self):
        fieldnames, rows = read_csv(CONTINUITY_PATH)
        self.assertTrue(CONTINUITY_COLUMNS.issubset(fieldnames))
        pins = [int(row["pin"]) for row in rows]
        self.assertEqual(pins, list(range(1, 41)))
        self.assertEqual(len(pins), len(set(pins)))
        for row in rows:
            pin = int(row["pin"])
            self.assertEqual(row["reference_host_identity"], self.canonical[pin]["reference_host_identity"])
            self.assertEqual(row["hat_net"], self.canonical[pin]["hat_net"])
        forbidden = {"beep", "yes", "no", "continuous", "continuity"}
        reading_columns = [name for name in fieldnames if name.endswith("_ohm")]
        for row in rows:
            self.assertFalse(forbidden.intersection(row[name].strip().lower() for name in reading_columns))

    def test_isolation_csv_is_exact_58_pair_physical_grid_record(self):
        fieldnames, rows = read_csv(ISOLATION_PATH)
        self.assertTrue(ISOLATION_COLUMNS.issubset(fieldnames))
        expected = physical_pairs()
        actual = [(row["pair_id"], int(row["pin_a"]), int(row["pin_b"])) for row in rows]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 58)
        self.assertEqual(len(actual), len(set(actual)))
        for row in rows:
            a, b = int(row["pin_a"]), int(row["pin_b"])
            self.assertEqual(row["pin_a_reference_host_identity"], self.canonical[a]["reference_host_identity"])
            self.assertEqual(row["pin_a_hat_net"], self.canonical[a]["hat_net"])
            self.assertEqual(row["pin_b_reference_host_identity"], self.canonical[b]["reference_host_identity"])
            self.assertEqual(row["pin_b_hat_net"], self.canonical[b]["hat_net"])
            expected_relation = "same_net" if self.canonical[a]["hat_net"] == self.canonical[b]["hat_net"] else "distinct_net"
            self.assertEqual(row["relation"], expected_relation)
            if expected_relation == "same_net":
                for name in ("premate_pass", "initial_pass", "pressure_pass", "post_remate_pass"):
                    self.assertEqual(row[name], "N/A")

    def test_plan_defines_numeric_continuity_method_and_probe_points(self):
        text = " ".join(PLAN_PATH.read_text(encoding="utf-8").lower().split())
        for phrase in (
            "exposed solder joint/pad of zero 3w header pin n on the host underside",
            "exposed outer toe of hat j4 smt land n",
            "shorted-lead resistance",
            "corrected resistance",
            "<= 1.0 ohm",
            "numeric",
            "bounded-pressure",
            "post-remate",
        ):
            self.assertIn(phrase, text)

    def test_plan_defines_adjacent_isolation_method_and_threshold(self):
        text = " ".join(PLAN_PATH.read_text(encoding="utf-8").lower().split())
        for phrase in (
            "20 cross-row pairs",
            "19 odd-column pairs",
            "19 even-column pairs",
            "exactly 58",
            "j4 outer toes",
            "exposed host underside header solder joints",
            "after 2 s stabilized",
            "> 50 ohm",
            "no sustained <= 50 ohm",
            "same-net pairs",
            "n/a",
            "fabrication_ready=false",
        ):
            self.assertIn(phrase, text)

    def test_preserved_sweep_has_bounded_evt_decision_and_geometry(self):
        data = json.loads(SWEEP_PATH.read_text(encoding="utf-8"))
        self.assertFalse(data["fabrication_ready"])
        self.assertEqual(data["measurement_type"], "CAD only, not physical")
        self.assertTrue(data["source_binding"]["unchanged_after_sweep"])
        decision = data["evt_stack_decision"]
        self.assertEqual(decision["surface_gap_mm"], 9.5)
        self.assertEqual(decision["fastener"], "M2")
        self.assertTrue(decision["physical_validation_required"])
        self.assertFalse(decision["fabrication_ready"])
        self.assertEqual(len(data["gaps"]), 8)
        self.assertEqual([row["surface_gap_mm"] for row in data["gaps"]], [4.0, 6.2, 6.5, 7.0, 8.0, 9.0, 9.5, 10.0])
        self.assertTrue(all(row["fabrication_ready"] is False for row in data["gaps"]))

        selected = next(row for row in data["gaps"] if row["surface_gap_mm"] == 9.5)
        axial = selected["axial_geometry"]
        self.assertTrue(math.isclose(axial["translation_z_mm"], 9.585, abs_tol=1e-6))
        self.assertTrue(math.isclose(axial["body_lower_face_minus_host_plastic_top_mm"], 3.3074, abs_tol=1e-6))
        self.assertTrue(math.isclose(axial["axial_entry_past_socket_lower_face_mm"], 2.6926, abs_tol=1e-6))
        self.assertEqual(selected["j4_low_header_region_intersection_mm3"], 0.0)
        for name in (
            "bottom_to_complete_host",
            "c45_to_complete_host",
            "c45_max_material_envelope_to_host",
            "substrate_to_complete_host",
        ):
            self.assertEqual(selected[name]["intersection_volume_mm3"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
