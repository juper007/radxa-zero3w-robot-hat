#!/usr/bin/env python3
"""Regression guard for intentionally removed PCB artwork."""

from pathlib import Path

PCB = Path(__file__).with_name("radxa_zero3w_robot_hat.kicad_pcb")
SCHEMATIC = Path(__file__).with_name("radxa_zero3w_robot_hat.kicad_sch")

FORBIDDEN_LOGO_IDENTIFIERS = {
    "Library_Pollen:Logo_Pollen_2021_sq": "Pollen Robotics",
    "DNP Logo Pollen 2021": "Pollen Robotics",
    "Library_Pollen:Logo_HF_2025": "Hugging Face",
    "Logo HF 2025": "Hugging Face",
}


def test_removed_brand_logos_are_absent() -> None:
    pcb = PCB.read_text(encoding="utf-8")
    found = {
        brand: identifier
        for identifier, brand in FORBIDDEN_LOGO_IDENTIFIERS.items()
        if identifier in pcb
    }
    assert not found, f"removed brand logo artwork remains on PCB: {found}"


def test_removed_brand_logo_symbols_are_absent() -> None:
    schematic = SCHEMATIC.read_text(encoding="utf-8")
    forbidden_symbols = {
        '(property "Reference" "H2"': "Hugging Face",
        '(property "Reference" "H3"': "Pollen Robotics",
    }
    found = {
        brand: marker
        for marker, brand in forbidden_symbols.items()
        if marker in schematic
    }
    assert not found, f"removed brand logo symbols remain in schematic: {found}"


def main() -> None:
    test_removed_brand_logos_are_absent()
    test_removed_brand_logo_symbols_are_absent()
    print("PCB ARTWORK POLICY TESTS: PASS")


if __name__ == "__main__":
    main()
