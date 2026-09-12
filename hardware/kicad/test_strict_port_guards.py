#!/usr/bin/env python3
"""Adversarial regression tests for strict-port fail-closed guards."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
CHECKER = Path("hardware/kicad/check_strict_port.py")


def copy_repository(directory: Path) -> Path:
    destination = directory / "repo"
    shutil.copytree(
        REPO,
        destination,
        ignore=shutil.ignore_patterns(".git", ".upstream", "__pycache__", "*.pyc"),
    )
    return destination


def run_checker(repository: Path, expected: str) -> None:
    result = subprocess.run(
        [sys.executable, str(repository / CHECKER)],
        cwd=repository,
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode == 0 or expected not in output:
        raise SystemExit(
            f"negative test unexpectedly passed or failed for the wrong reason; "
            f"expected {expected!r}\n{output}"
        )


def sexpr_block(text: str, kind: str, ref: str) -> tuple[int, int]:
    marker = f'(property "Reference" "{ref}"'
    position = text.find(marker)
    if position < 0:
        raise ValueError(f"missing {ref}")
    start = text.rfind(f"\n\t({kind}", 0, position)
    if start < 0:
        raise ValueError(f"missing {kind} block for {ref}")
    depth = 0
    for index in range(start + 1, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(f"unterminated {kind} block for {ref}")


def change_r1_value(path: Path, kind: str) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = sexpr_block(text, kind, "R1")
    block = text[start:end]
    old = '(property "Value" "10k"'
    if block.count(old) != 1:
        raise ValueError(f"unexpected R1 value in {path}")
    block = block.replace(old, '(property "Value" "11k"', 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def test_policy_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-policy-") as directory:
        repository = copy_repository(Path(directory))
        project = repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pro"
        text = project.read_text(encoding="utf-8")
        old = '"shorting_items": "error"'
        if text.count(old) != 1:
            raise ValueError("unexpected shorting_items policy")
        project.write_text(text.replace(old, '"shorting_items": "ignore"', 1), encoding="utf-8")
        run_checker(repository, "ERC/DRC rule, constraint, or exclusion policy changed")


def test_erc_pin_map_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-pin-map-") as directory:
        repository = copy_repository(Path(directory))
        project_path = repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pro"
        project = json.loads(project_path.read_text(encoding="utf-8"))
        before = project["erc"]["pin_map"][0][11]
        project["erc"]["pin_map"][0][11] = 0 if before != 0 else 1
        project_path.write_text(json.dumps(project), encoding="utf-8")
        run_checker(repository, "ERC/DRC rule, constraint, or exclusion policy changed")


def test_baseline_hash_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-baseline-") as directory:
        repository = copy_repository(Path(directory))
        baseline = repository / "validation/strict_port/upstream_baseline_netlist.xml"
        baseline.write_bytes(baseline.read_bytes() + b"\n")
        run_checker(repository, "pinned upstream baseline changed")


def test_bom_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-bom-") as directory:
        repository = copy_repository(Path(directory))
        change_r1_value(repository / "hardware/kicad/audio.kicad_sch", "symbol")
        change_r1_value(
            repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb",
            "footprint",
        )
        netlist = repository / "validation/strict_port/radxa_port_netlist.xml"
        tree = ET.parse(netlist)
        component = next(
            row
            for row in tree.getroot().findall("./components/comp")
            if row.get("ref") == "R1"
        )
        component.find("value").text = "11k"
        tree.write(netlist, encoding="UTF-8", xml_declaration=True)
        run_checker(repository, "component value or footprint drift versus upstream")


def test_j4_geometry_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-j4-geometry-") as directory:
        repository = copy_repository(Path(directory))
        board = repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb"
        text = board.read_text(encoding="utf-8")
        start, end = sexpr_block(text, "footprint", "J4")
        block = text[start:end]
        old = "(size 1.02 1.8)"
        if block.count(old) != 40:
            raise ValueError("unexpected J4 DRC-clean candidate pad geometry")
        block = block.replace(old, "(size 1.02 2)", 1)
        board.write_text(text[:start] + block + text[end:], encoding="utf-8")
        run_checker(repository, "J4 footprint differs from the qualified DRC-clean candidate")


def test_j4_placement_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-j4-placement-") as directory:
        repository = copy_repository(Path(directory))
        board = repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb"
        text = board.read_text(encoding="utf-8")
        original = '(footprint "Library_Pollen:PinHeader_2x20_P2.54mm_Vertical_with_rasp_HAT_zero_SMD_connector"\n\t\t(layer "B.Cu")'
        replacement = original.replace('"B.Cu"', '"F.Cu"')
        if text.count(original) != 1:
            raise SystemExit("J4 placement negative test could not locate exactly one footprint")
        board.write_text(text.replace(original, replacement, 1), encoding="utf-8")
        run_checker(repository, "J4 footprint differs from the qualified DRC-clean candidate")


def test_j4_pad_attribute_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-j4-pad-attribute-") as directory:
        repository = copy_repository(Path(directory))
        board = repository / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb"
        text = board.read_text(encoding="utf-8")
        start = text.index('\t\t(pad "1" smd rect', text.index('(property "Reference" "J4"'))
        uuid_pos = text.index('\n\t\t\t(uuid ', start)
        text = text[:uuid_pos] + '\n\t\t\t(solder_paste_margin -0.89)' + text[uuid_pos:]
        board.write_text(text, encoding="utf-8")
        run_checker(repository, "J4 footprint differs from the qualified DRC-clean candidate")


def test_j4_quoted_property_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-j4-quoted-property-") as directory:
        repository = copy_repository(Path(directory))
        board = repository / "hardware" / "kicad" / "radxa_zero3w_robot_hat.kicad_pcb"
        text = board.read_text(encoding="utf-8")
        old = '2x20 2.54 mm surface-mount bottom-entry pass-through socket with PCB pegs'
        new = '2x20  2.54 mm surface-mount bottom-entry pass-through socket with PCB pegs'
        if text.count(old) != 2:
            raise ValueError("unexpected J4 description inventory")
        board.write_text(text.replace(old, new, 1), encoding="utf-8")
        run_checker(repository, "J4 footprint differs from the qualified DRC-clean candidate")


def test_j4_identity_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-j4-identity-") as directory:
        repository = copy_repository(Path(directory))
        schematic = repository / "hardware" / "kicad" / "main.kicad_sch"
        text = schematic.read_text(encoding="utf-8")
        old = '(property "Manufacturer_Part_Number" "REF-182665-01"'
        new = '(property "Manufacturer_Part_Number" "C2685112"'
        if text.count(old) != 1:
            raise ValueError("unexpected J4 manufacturer-part property inventory")
        schematic.write_text(text.replace(old, new, 1), encoding="utf-8")
        run_checker(repository, "J4 manufacturing identity changed")


def test_unconnected_evidence_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="strict-unconnected-") as directory:
        repository = copy_repository(Path(directory))
        report_path = repository / "validation/strict_port/radxa_port_drc.json"
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        report["unconnected_items"].append(
            {
                "description": "adversarial stale evidence",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "pos": {"x": 0.0, "y": 0.0},
            }
        )
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        run_checker(repository, "committed DRC unconnected items are stale")


def main() -> None:
    test_policy_guard()
    test_erc_pin_map_guard()
    test_baseline_hash_guard()
    test_bom_guard()
    test_j4_geometry_guard()
    test_j4_placement_guard()
    test_j4_pad_attribute_guard()
    test_j4_quoted_property_guard()
    test_j4_identity_guard()
    test_unconnected_evidence_guard()
    print("STRICT PORT NEGATIVE TESTS: PASS")


if __name__ == "__main__":
    main()
