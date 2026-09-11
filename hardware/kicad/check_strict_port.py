#!/usr/bin/env python3
"""Regenerate and validate the single-board Radxa ZERO 3W strict port."""

from collections import Counter
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SCH = ROOT / "radxa_zero3w_robot_hat.kicad_sch"
PCB = ROOT / "radxa_zero3w_robot_hat.kicad_pcb"
COMMITTED_NETLIST = REPO / "validation/strict_port/radxa_port_netlist.xml"
BASE_DRC = REPO / "validation/strict_port/upstream_baseline_drc.json"
COMMITTED_PORT_DRC = REPO / "validation/strict_port/radxa_port_drc.json"
BASE_ERC = REPO / "validation/strict_port/upstream_baseline_erc.json"
COMMITTED_PORT_ERC = REPO / "validation/strict_port/radxa_port_erc.json"
SUMMARY = REPO / "validation/strict_port/report_summary.json"


def fail(message: str) -> None:
    raise SystemExit(f"STRICT PORT CHECK: FAIL — {message}")


def find_kicad_cli() -> str:
    configured = os.environ.get("KICAD_CLI")
    if configured and Path(configured).is_file():
        return configured
    discovered = shutil.which("kicad-cli")
    if discovered:
        return discovered
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates = sorted(
            (Path(local_app_data) / "Programs" / "KiCad").glob("*/bin/kicad-cli.exe"),
            reverse=True,
        )
        if candidates:
            return str(candidates[0])
    fail("kicad-cli was not found; set KICAD_CLI or install KiCad 10")
    return ""


def run_kicad(cli: str, arguments: list[str]) -> None:
    result = subprocess.run(
        [cli, *arguments],
        cwd=REPO,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        fail(
            f"kicad-cli failed ({result.returncode}): {' '.join(arguments)}\n"
            f"{result.stdout}\n{result.stderr}"
        )


def symbol_block(text: str, ref: str) -> str:
    marker = f'(property "Reference" "{ref}"'
    pos = text.find(marker)
    if pos < 0:
        fail(f"missing schematic reference {ref}")
    start = text.rfind("\n\t(symbol", 0, pos)
    if start < 0:
        fail(f"cannot locate symbol block for {ref}")
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    fail(f"unterminated symbol block for {ref}")
    return ""


def footprint_block(text: str, ref: str) -> str:
    marker = f'(property "Reference" "{ref}"'
    pos = text.find(marker)
    if pos < 0:
        fail(f"missing PCB reference {ref}")
    start = text.rfind("\n\t(footprint", 0, pos)
    if start < 0:
        fail(f"cannot locate footprint block for {ref}")
    depth = 0
    for index in range(start + 1, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    fail(f"unterminated footprint block for {ref}")
    return ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def item_identity(item: dict) -> tuple:
    pos = item.get("pos") or {}
    return (
        item.get("uuid"),
        pos.get("x"),
        pos.get("y"),
    )


def finding_identity(finding: dict) -> tuple:
    return (
        finding.get("type"),
        finding.get("severity"),
        tuple(sorted(item_identity(item) for item in finding.get("items", []))),
    )


def finding_counter(findings: list[dict]) -> Counter:
    return Counter(finding_identity(finding) for finding in findings)


def erc_findings(report: dict) -> list[dict]:
    return [
        violation
        for sheet in report.get("sheets", [])
        for violation in sheet.get("violations", [])
    ]


def netlist_signature(path: Path) -> tuple:
    root = ET.parse(path).getroot()
    components = tuple(
        sorted(
            (
                component.get("ref") or component.findtext("ref") or "",
                component.findtext("value") or "",
                component.findtext("footprint") or "",
            )
            for component in root.findall("./components/comp")
        )
    )
    nets = tuple(
        sorted(
            (
                net.get("name", ""),
                tuple(
                    sorted(
                        (
                            node.get("ref", ""),
                            node.get("pin", ""),
                            node.get("pinfunction", ""),
                            node.get("pintype", ""),
                        )
                        for node in net.findall("node")
                    )
                ),
            )
            for net in root.findall("./nets/net")
        )
    )
    return components, nets


for path in (
    SCH,
    PCB,
    COMMITTED_NETLIST,
    BASE_DRC,
    COMMITTED_PORT_DRC,
    BASE_ERC,
    COMMITTED_PORT_ERC,
    SUMMARY,
):
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(REPO)}")

if any(ROOT.glob("*daughterboard*")):
    fail("daughterboard artifact exists in the active strict-port branch")

sch_text = SCH.read_text(encoding="utf-8")
pcb_text = PCB.read_text(encoding="utf-8")
all_schematic_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in [
        SCH,
        ROOT / "main.kicad_sch",
        ROOT / "audio.kicad_sch",
        ROOT / "dynamixel.kicad_sch",
        ROOT / "sensors.kicad_sch",
    ]
)

if "Radxa ZERO 3W Robot HAT" not in sch_text:
    fail("Radxa project identity missing from top-level schematic")
if "Radxa_Z3W_HAT\\nASE01187-C1" not in pcb_text:
    fail("Radxa derivative identity missing from PCB silkscreen")

required_nets = {
    "I2C3_SDA_M0",
    "I2C3_SCL_M0",
    "UART2_TX_M0",
    "UART2_RX_M0",
    "I2S3_SCLK_M0",
    "I2S3_LRCK_M0",
    "I2S3_SDI_M0",
    "I2S3_SDO_M0",
}
missing = sorted(
    net for net in required_nets if net not in all_schematic_text or net not in pcb_text
)
if missing:
    fail(f"critical Radxa nets missing from schematic or PCB: {missing}")

for ref, source in (
    ("U4", ROOT / "main.kicad_sch"),
    ("J6", ROOT / "sensors.kicad_sch"),
    ("J7", ROOT / "sensors.kicad_sch"),
    ("J8", ROOT / "sensors.kicad_sch"),
):
    if "(dnp yes)" not in symbol_block(source.read_text(encoding="utf-8"), ref):
        fail(f"{ref} must remain DNP")
    pcb_block = footprint_block(pcb_text, ref)
    if "(attr smd dnp)" not in pcb_block and "(attr through_hole dnp)" not in pcb_block:
        fail(f"PCB footprint {ref} must remain DNP")

cli = find_kicad_cli()
with tempfile.TemporaryDirectory(prefix="strict-port-") as directory:
    temporary = Path(directory)
    fresh_erc_path = temporary / "radxa_port_erc.json"
    fresh_drc_path = temporary / "radxa_port_drc.json"
    fresh_netlist_path = temporary / "radxa_port_netlist.xml"
    run_kicad(
        cli,
        ["sch", "erc", "--format", "json", "--severity-all", "-o", str(fresh_erc_path), str(SCH)],
    )
    run_kicad(
        cli,
        ["sch", "export", "netlist", "--format", "kicadxml", "-o", str(fresh_netlist_path), str(SCH)],
    )
    run_kicad(
        cli,
        [
            "pcb",
            "drc",
            "--format",
            "json",
            "--severity-all",
            "--schematic-parity",
            "-o",
            str(fresh_drc_path),
            str(PCB),
        ],
    )

    if netlist_signature(fresh_netlist_path) != netlist_signature(COMMITTED_NETLIST):
        fail("committed Radxa netlist is stale relative to the current schematic")

    fresh_root = ET.parse(fresh_netlist_path).getroot()
    components = fresh_root.findall("./components/comp")
    nets = fresh_root.findall("./nets/net")
    if len(components) != 128 or len(nets) != 95:
        fail(f"unexpected netlist size: {len(components)} components / {len(nets)} nets")

    expected_header = {
        1: "+3V3",
        2: "+5V",
        3: "I2C3_SDA_M0",
        4: "+5V",
        5: "I2C3_SCL_M0",
        6: "GND",
        8: "UART2_TX_M0",
        9: "GND",
        10: "UART2_RX_M0",
        12: "I2S3_SCLK_M0",
        14: "GND",
        17: "+3V3",
        20: "GND",
        25: "GND",
        30: "GND",
        34: "GND",
        35: "I2S3_LRCK_M0",
        38: "I2S3_SDI_M0",
        39: "GND",
        40: "I2S3_SDO_M0",
    }
    actual_header = {}
    for net in nets:
        for node in net.findall("node"):
            pin = node.get("pin", "")
            if node.get("ref") == "J4" and pin.isdigit() and int(pin) in expected_header:
                actual_header[int(pin)] = net.get("name", "").rsplit("/", 1)[-1]
    if actual_header != expected_header:
        fail(f"J4 mapping mismatch: {actual_header}")

    base_drc = load_json(BASE_DRC)
    committed_drc = load_json(COMMITTED_PORT_DRC)
    fresh_drc = load_json(fresh_drc_path)
    base_drc_findings = finding_counter(base_drc.get("violations", []))
    fresh_drc_findings = finding_counter(fresh_drc.get("violations", []))
    if fresh_drc_findings != base_drc_findings:
        fail("fresh DRC findings differ from the normalized upstream baseline")
    if finding_counter(committed_drc.get("violations", [])) != fresh_drc_findings:
        fail("committed Radxa DRC report is stale relative to the current PCB")
    if fresh_drc.get("unconnected_items"):
        fail("routed PCB has unconnected items")

    base_parity = finding_counter(base_drc.get("schematic_parity", []))
    fresh_parity = finding_counter(fresh_drc.get("schematic_parity", []))
    if fresh_parity != base_parity:
        fail("fresh schematic-parity findings differ from the normalized upstream baseline")
    if finding_counter(committed_drc.get("schematic_parity", [])) != fresh_parity:
        fail("committed schematic-parity report is stale relative to the current design")

    base_erc = load_json(BASE_ERC)
    committed_erc = load_json(COMMITTED_PORT_ERC)
    fresh_erc = load_json(fresh_erc_path)
    base_erc_findings = finding_counter(erc_findings(base_erc))
    fresh_erc_findings = finding_counter(erc_findings(fresh_erc))
    if fresh_erc_findings != base_erc_findings:
        fail("fresh ERC findings differ from the normalized upstream baseline")
    if finding_counter(erc_findings(committed_erc)) != fresh_erc_findings:
        fail("committed Radxa ERC report is stale relative to the current schematic")

summary = load_json(SUMMARY)
expected_summary = {
    "board_count": 1,
    "outline_mm": [65.05, 30.95],
    "footprints": 127,
    "tracks": 1021,
    "erc_total": 55,
    "erc_new": 0,
    "drc_total": 49,
    "drc_new": 0,
    "parity_total": 111,
    "parity_new": 0,
}
actual_summary = {
    "board_count": summary["architecture"]["board_count"],
    "outline_mm": summary["architecture"]["outline_mm"],
    "footprints": summary["pcb"]["footprints"],
    "tracks": summary["pcb"]["tracks"],
    "erc_total": summary["erc_baseline"]["total"],
    "erc_new": summary["erc_baseline"]["new_vs_upstream"],
    "drc_total": summary["drc_baseline"]["total"],
    "drc_new": summary["drc_baseline"]["new_vs_upstream"],
    "parity_total": summary["schematic_parity_baseline"]["total"],
    "parity_new": summary["schematic_parity_baseline"]["new_vs_upstream"],
}
if actual_summary != expected_summary or summary.get("fabrication_ready") is not False:
    fail(f"summary mismatch: {actual_summary}")

print("STRICT PORT CHECK: PASS")
print(
    "Regenerated KiCad ERC/DRC/parity/netlist evidence and validated one "
    "65.05 x 30.95 mm routed HAT with no new findings versus upstream."
)
