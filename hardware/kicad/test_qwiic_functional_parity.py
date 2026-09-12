#!/usr/bin/env python3
"""Functional-parity checks for the four original Qwiic ports."""

from __future__ import annotations

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
KICAD = REPO / "hardware/kicad"
DOCS = REPO / "docs"
SCHEMATIC = KICAD / "sensors.kicad_sch"
PCB = KICAD / "radxa_zero3w_robot_hat.kicad_pcb"
NETLIST = REPO / "validation/strict_port/radxa_port_netlist.xml"
REPORT_SUMMARY = REPO / "validation/strict_port/report_summary.json"
OVERLAY = REPO / "software/overlays/radxa-zero3w-robot-hat-qwiic.dts"

POPULATED = {
    "J5": "JST SH",
    "J6": "JST SH",
    "J7": "JST SH",
    "J8": "JST SH",
    "R18": "0R",
    "R19": "0R",
    "R20": "10k",
    "R21": "10k",
    "R34": "10k",
    "R35": "10k",
    "R38": "10k",
    "R39": "10k",
}

QWIIC_NETS = {
    "J5": {
        "1": "GND",
        "2": "+3V3",
        "3": "/Schematic/Audio/I2C3_SDA_M0",
        "4": "/Schematic/Audio/I2C3_SCL_M0",
    },
    "J6": {"1": "GND", "2": "+3V3", "3": "Net-(J6-Pin_3)", "4": "Net-(J6-Pin_4)"},
    "J7": {
        "1": "GND",
        "2": "+3V3",
        "3": "/Schematic/Audio/GPIO4_C6_P24",
        "4": "/Schematic/Audio/GPIO4_C5_P21",
    },
    "J8": {
        "1": "GND",
        "2": "+3V3",
        "3": "/Schematic/Audio/GPIO4_C3_P19",
        "4": "/Schematic/Audio/GPIO4_C2_P23",
    },
}

J6_LINK_NETS = {
    "R18": {"1": "/Schematic/Audio/GPIO3_C4_P7", "2": "Net-(J6-Pin_3)"},
    "R19": {"1": "/Schematic/Audio/GPIO3_B3_P29", "2": "Net-(J6-Pin_4)"},
}

PULL_UP_NETS = {
    "R20": {"1": "+3V3", "2": "Net-(J6-Pin_3)"},
    "R21": {"1": "+3V3", "2": "Net-(J6-Pin_4)"},
    "R34": {"1": "+3V3", "2": "/Schematic/Audio/GPIO4_C6_P24"},
    "R35": {"1": "+3V3", "2": "/Schematic/Audio/GPIO4_C5_P21"},
    "R38": {"1": "+3V3", "2": "/Schematic/Audio/GPIO4_C3_P19"},
    "R39": {"1": "+3V3", "2": "/Schematic/Audio/GPIO4_C2_P23"},
}

OVERLAY_GPIO_PAIRS = {
    "j6": ("gpio3", "RK_PC4", "gpio3", "RK_PB3"),
    "j7": ("gpio4", "RK_PC6", "gpio4", "RK_PC5"),
    "j8": ("gpio4", "RK_PC3", "gpio4", "RK_PC2"),
}

UPSTREAM_DNP = {"C25", "R10", "R11", "R16", "R17", "R36", "R37", "R41", "U4"}


def sexpr_block(text: str, kind: str, ref: str) -> str:
    marker = f'(property "Reference" "{ref}"'
    position = text.find(marker)
    if position < 0:
        raise AssertionError(f"missing {ref}")
    start = text.rfind(f"\n\t({kind}", 0, position)
    if start < 0:
        raise AssertionError(f"missing {kind} block for {ref}")
    depth = 0
    for index in range(start + 1, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError(f"unterminated {kind} block for {ref}")


def property_value(block: str, name: str) -> str:
    match = re.search(rf'\(property "{re.escape(name)}" "([^"]*)"', block)
    if not match:
        raise AssertionError(f"missing property {name}")
    return match.group(1)


def test_original_qwiic_parts_are_populated() -> None:
    schematic = SCHEMATIC.read_text(encoding="utf-8")
    pcb = PCB.read_text(encoding="utf-8")
    for ref, value in POPULATED.items():
        symbol = sexpr_block(schematic, "symbol", ref)
        footprint = sexpr_block(pcb, "footprint", ref)
        assert "(dnp no)" in symbol, f"{ref} must be populated in the schematic"
        assert not re.search(r"\(attr [^)]*\bdnp\b", footprint), f"{ref} must be populated on the PCB"
        assert property_value(symbol, "Value") == value
        assert property_value(footprint, "Value") == value


def test_qwiic_signal_pin_routes_match_the_preserved_board() -> None:
    root = ET.parse(NETLIST).getroot()
    actual: dict[str, dict[str, str]] = {ref: {} for ref in QWIIC_NETS}
    links: dict[str, dict[str, str]] = {ref: {} for ref in J6_LINK_NETS}
    pull_ups: dict[str, dict[str, str]] = {ref: {} for ref in PULL_UP_NETS}
    for net in root.findall("./nets/net"):
        name = net.get("name", "")
        for node in net.findall("node"):
            ref = node.get("ref", "")
            pin = node.get("pin", "")
            if ref in actual and pin in {"1", "2", "3", "4"}:
                actual[ref][pin] = name
            if ref in links and pin in {"1", "2"}:
                links[ref][pin] = name
            if ref in pull_ups and pin in {"1", "2"}:
                pull_ups[ref][pin] = name
    assert actual == QWIIC_NETS
    assert links == J6_LINK_NETS
    assert pull_ups == PULL_UP_NETS


def test_radxa_overlay_exposes_three_independent_gpio_i2c_buses() -> None:
    overlay = OVERLAY.read_text(encoding="utf-8")
    assert "&{/} {" in overlay, "overlay must target the base tree root"
    assert 'compatible = "radxa,zero-3w", "rockchip,rk3566";' in overlay
    for index, (name, pins) in enumerate(OVERLAY_GPIO_PAIRS.items(), start=10):
        sda_controller, sda_pin, scl_controller, scl_pin = pins
        node_match = re.search(rf"qwiic_{name}: i2c-gpio-{name} \{{(.*?)\n\t\}};", overlay, re.DOTALL)
        assert node_match, f"missing i2c-gpio node for {name}"
        node = node_match.group(1)
        assert f'i2c{index} = "/i2c-gpio-{name}";' in overlay
        assert f"sda-gpios = <&{sda_controller} {sda_pin}" in node
        assert f"scl-gpios = <&{scl_controller} {scl_pin}" in node
        assert "i2c-gpio,delay-us = <5>;" in node


def test_status_reports_exact_upstream_dnp_set() -> None:
    summary = json.loads(REPORT_SUMMARY.read_text(encoding="utf-8"))
    assert set(summary["dnp_options"]) == UPSTREAM_DNP
    parity = summary["qwiic_functional_parity"]
    assert {"J5", "J6", "J7", "J8"}.issubset(parity["populated"])


def test_docs_do_not_retain_obsolete_qwiic_dnp_policy() -> None:
    stale = []
    for path in DOCS.rglob("*.md"):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "isolated by DNP" in line or "isolated from unqualified Qwiic pull-ups and connectors" in line:
                stale.append(f"{path.relative_to(REPO)}:{line_number}")
    top_schematic = KICAD / "radxa_zero3w_robot_hat.kicad_sch"
    for line_number, line in enumerate(top_schematic.read_text(encoding="utf-8").splitlines(), start=1):
        if "auxiliary Qwiic connectors J6/J7/J8: DNP" in line:
            stale.append(f"{top_schematic.relative_to(REPO)}:{line_number}")
    assert not stale, f"obsolete Qwiic DNP policy remains in {stale}"


def main() -> None:
    test_original_qwiic_parts_are_populated()
    test_qwiic_signal_pin_routes_match_the_preserved_board()
    test_radxa_overlay_exposes_three_independent_gpio_i2c_buses()
    test_status_reports_exact_upstream_dnp_set()
    test_docs_do_not_retain_obsolete_qwiic_dnp_policy()
    print("QWIIC FUNCTIONAL PARITY TESTS: PASS")


if __name__ == "__main__":
    main()
