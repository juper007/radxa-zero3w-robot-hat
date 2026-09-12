#!/usr/bin/env python3
"""Regenerate and validate the single-board Radxa ZERO 3W strict port."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SCH = ROOT / "radxa_zero3w_robot_hat.kicad_sch"
PCB = ROOT / "radxa_zero3w_robot_hat.kicad_pcb"
PRO = ROOT / "radxa_zero3w_robot_hat.kicad_pro"
COMMITTED_NETLIST = REPO / "validation/strict_port/radxa_port_netlist.xml"
BASE_NETLIST = REPO / "validation/strict_port/upstream_baseline_netlist.xml"
BASE_DRC = REPO / "validation/strict_port/upstream_baseline_drc.json"
COMMITTED_PORT_DRC = REPO / "validation/strict_port/radxa_port_drc.json"
BASE_ERC = REPO / "validation/strict_port/upstream_baseline_erc.json"
COMMITTED_PORT_ERC = REPO / "validation/strict_port/radxa_port_erc.json"
SUMMARY = REPO / "validation/strict_port/report_summary.json"
KICAD_VERSION = "10.0.6"
UPSTREAM_COMMIT = "23eab11927f95ceca0dfa35bf182caeb7db39ea0"
BASELINE_SHA256 = {
    BASE_NETLIST: "210a52c16572f7fcace0787d3f79f60838254019671c4edae41a4ec6a69ede33",
    BASE_ERC: "f50ccd9ea357dbe3f051d5032b9b2796a7255726f048cde3878973ce5e84df44",
    BASE_DRC: "740242aa80c1aa71d9332f64400b382c4a1001b63ab529777bb7625d22cfad18",
}
PROJECT_POLICY_SHA256 = "4adff66c71b09e7c04e35641b1ac3bcad518250f7eb9362f8f85f625805de698"
EDGE_CUTS_SHA256 = "69787bc712e9b43c4ff232a5ceb72b5bce5a73ea0f5e7b6548bc5b64c4cb33bf"
J4_FOOTPRINT_SHA256 = "653abbdf65d2e09a9d4f49745931e88c6ff32736958e08071b72692091ac2039"
POWER_REGION_SHA256 = "b3cdfb6456a747281ee42a346d4d0420079616a3159b70a3f8aa6cb9b3f7f079"
FILLED_ZONE_SHA256 = "e97175d477adf4ce9c3c16561b6130983807780dbf025033157494f3d8ffe8ec"
EXPECTED_DRC_IGNORES = {
    "footprint_filters_mismatch",
    "footprint_type_mismatch",
    "missing_courtyard",
    "npth_inside_courtyard",
    "pth_inside_courtyard",
    "track_not_centered_on_via",
    "tuning_profile_track_geometries",
}
EXPECTED_ERC_IGNORES = {
    "footprint_filter",
    "four_way_junction",
    "simulation_model_issue",
    "single_global_label",
}
ALLOWED_ADDED_COMPONENTS = {
    "C45": ("10uF 50V X7R", "Capacitor_SMD:C_1210_3225Metric"),
}
ALLOWED_COMPONENT_VALUES = {
    "C21": ("22u 6V3", "22u 10V"),
    "C22": ("22u 6V3", "22u 10V"),
    "J4": ("Female Header 2x20 SMD", "Radxa ZERO 3W 2x20 HAT Header"),
    "R18": ("0R", "DNP-0R"),
    "R19": ("0R", "DNP-0R"),
    "R20": ("10k", "DNP-10k"),
    "R21": ("10k", "DNP-10k"),
    "R34": ("10k", "DNP-10k"),
    "R35": ("10k", "DNP-10k"),
    "R38": ("10k", "DNP-10k"),
    "R39": ("10k", "DNP-10k"),
}


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
            (Path(local_app_data) / "Programs" / "KiCad").glob("*/bin/kicad-cli.exe")
        )
        exact = [candidate for candidate in candidates if candidate.parents[1].name == "10.0"]
        if exact:
            return str(exact[-1])
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


def require_kicad_version(cli: str) -> None:
    result = subprocess.run(
        [cli, "--version"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    version = result.stdout.strip()
    if result.returncode != 0 or version != KICAD_VERSION:
        fail(f"KiCad {KICAD_VERSION} is required; detected {version or 'unknown'}")


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


def property_value(block: str, name: str) -> str:
    match = re.search(rf'\(property "{re.escape(name)}" "([^"]*)"', block)
    if not match:
        fail(f"missing {name} property")
    return match.group(1)


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


def child_blocks(text: str, kind: str) -> list[str]:
    blocks = []
    cursor = 0
    marker = f"({kind} "
    while True:
        start = text.find(marker, cursor)
        if start < 0:
            return blocks
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    cursor = index + 1
                    break
        else:
            fail(f"unterminated {kind} block")


def j4_pad_geometry(footprint: str) -> tuple[str, set[str]]:
    footprint_layer = re.search(r'^\s*\(footprint "[^"]+"\s+\(layer "([^"]+)"\)', footprint)
    footprint_at = re.search(r'^\s*\(footprint "[^"]+".*?\n\s*\(at ([^)]+)\)', footprint, re.DOTALL)
    if not footprint_layer or not footprint_at:
        fail("malformed J4 footprint placement")

    rows = []
    uuids = set()
    for block in child_blocks(footprint, "pad"):
        header = re.match(r'\(pad "([^"]*)" (\S+) (\S+)', block)
        if not header:
            fail("malformed J4 pad block")

        def values(key: str) -> list[str]:
            match = re.search(rf"\({key} ([^)]+)\)", block)
            return match.group(1).split() if match else []

        rows.append([
            header.group(1),
            header.group(2),
            header.group(3),
            values("at"),
            values("size"),
            values("drill"),
            values("layers"),
        ])
        uuid = re.search(r'\(uuid "([^"]+)"\)', block)
        if not uuid:
            fail("J4 pad UUID is missing")
        uuids.add(uuid.group(1))
    if len(rows) != 86 or len(uuids) != 86:
        fail("unexpected J4 pad inventory")
    return hashlib.sha256(footprint.lstrip().encode()).hexdigest(), uuids


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    # Git stores these text artifacts with LF; normalize Windows worktree CRLF.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def project_policy(project: dict) -> dict:
    design = project["board"]["design_settings"]
    return {
        "board": {
            key: design[key]
            for key in ("drc_exclusions", "rule_severities", "rules")
        },
        "erc": {
            key: project["erc"][key]
            for key in ("erc_exclusions", "pin_map", "rule_severities")
        },
    }


def validate_report_contract(
    report: dict,
    *,
    kind: str,
    source: str,
    ignored: set[str],
) -> None:
    schema = f"https://schemas.kicad.org/{kind}.v1.json"
    required = {
        "$schema",
        "coordinate_units",
        "date",
        "ignored_checks",
        "included_severities",
        "kicad_version",
        "source",
    }
    if not required.issubset(report):
        fail(f"{kind.upper()} report is incomplete")
    if report["$schema"] != schema or report["coordinate_units"] != "mm":
        fail(f"unexpected {kind.upper()} report schema or coordinate units")
    if report["kicad_version"] != KICAD_VERSION:
        fail(f"unexpected {kind.upper()} report KiCad version")
    if not isinstance(report["date"], str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", report["date"]
    ):
        fail(f"unexpected {kind.upper()} report generation date")
    if Path(report["source"]).name != source:
        fail(f"unexpected {kind.upper()} report source: {report['source']}")
    if set(report["included_severities"]) != {"error", "warning", "exclusion"}:
        fail(f"unexpected {kind.upper()} included severities")
    ignored_rows = report["ignored_checks"]
    if {row.get("key") for row in ignored_rows} != ignored:
        fail(f"{kind.upper()} ignored-check policy changed")
    if any(not row.get("description") for row in ignored_rows):
        fail(f"{kind.upper()} ignored-check descriptions are incomplete")
    if kind == "erc":
        findings = erc_findings(report)
        if "sheets" not in report or any("violations" not in sheet for sheet in report["sheets"]):
            fail("ERC report sheet data is incomplete")
    else:
        for key in ("violations", "schematic_parity", "unconnected_items"):
            if key not in report:
                fail(f"DRC report is missing {key}")
        findings = report["violations"] + report["schematic_parity"]
        for item in report["unconnected_items"]:
            if not item.get("description") or not item.get("uuid") or not item.get("pos"):
                fail("DRC unconnected-item metadata is incomplete")
    for finding in findings:
        if not finding.get("description") or not finding.get("type") or not finding.get("severity"):
            fail(f"{kind.upper()} finding metadata is incomplete")
        for item in finding.get("items", []):
            if not item.get("description") or not item.get("uuid") or not item.get("pos"):
                fail(f"{kind.upper()} finding item metadata is incomplete")


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


def type_counts(rows: list[dict]) -> dict[str, int]:
    return dict(sorted(Counter(row["type"] for row in rows).items()))


def severity_counts(rows: list[dict]) -> Counter:
    return Counter(row["severity"] for row in rows)


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


def component_map(path: Path) -> dict[str, tuple[str, str]]:
    root = ET.parse(path).getroot()
    return {
        component.get("ref", ""): (
            component.findtext("value") or "",
            component.findtext("footprint") or "",
        )
        for component in root.findall("./components/comp")
    }


def net_memberships(path: Path) -> set[tuple[tuple[str, str, str, str], ...]]:
    root = ET.parse(path).getroot()
    return {
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
        )
        for net in root.findall("./nets/net")
    }


def validate_upstream_netlist(base: Path, port: Path) -> None:
    base_components = component_map(base)
    port_components = component_map(port)
    added = set(port_components) - set(base_components)
    removed = set(base_components) - set(port_components)
    if added != set(ALLOWED_ADDED_COMPONENTS) or removed:
        fail(f"component references differ from upstream: added={sorted(added)}, removed={sorted(removed)}")
    for ref, expected_component in ALLOWED_ADDED_COMPONENTS.items():
        if port_components[ref] != expected_component:
            fail(f"added component identity changed: {ref}")
    differences = {
        ref: (base_components[ref], port_components[ref])
        for ref in base_components
        if base_components[ref] != port_components[ref]
    }
    expected = {
        ref: ((before, base_components[ref][1]), (after, base_components[ref][1]))
        for ref, (before, after) in ALLOWED_COMPONENT_VALUES.items()
    }
    if differences != expected:
        fail(f"component value or footprint drift versus upstream: {differences}")
    base_memberships = net_memberships(base)
    port_memberships = net_memberships(port)
    port_root = ET.parse(port).getroot()
    c45_nodes = {
        net.get("name", ""): {(node.get("ref", ""), node.get("pin", "")) for node in net.findall("node") if node.get("ref") == "C45"}
        for net in port_root.findall("./nets/net")
        if any(node.get("ref") == "C45" for node in net.findall("node"))
    }
    if c45_nodes != {"+BATT": {("C45", "1")}, "GND": {("C45", "2")}}:
        fail(f"C45 net membership changed: {c45_nodes}")
    normalized_port_memberships = {
        tuple(node for node in nodes if node[0] != "C45")
        for nodes in port_memberships
    }
    if base_memberships != normalized_port_memberships:
        fail("electrical net membership differs from upstream")


def top_level_blocks(text: str, keyword: str) -> list[str]:
    blocks = []
    for match in re.finditer(rf"^\t\({re.escape(keyword)}\s", text, re.MULTILINE):
        start = match.start()
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    break
    return blocks


def board_metrics(text: str) -> dict:
    edge_blocks = [
        block
        for keyword in ("gr_line", "gr_arc", "gr_circle", "gr_rect")
        for block in top_level_blocks(text, keyword)
        if '(layer "Edge.Cuts")' in block
    ]
    points = [
        (float(match.group(1)), float(match.group(2)))
        for block in edge_blocks
        for match in re.finditer(
            r"\((?:start|mid|end|center)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\)",
            block,
        )
    ]
    if not points:
        fail("cannot derive the PCB outline from current Edge.Cuts geometry")
    outline = [
        round(max(x for x, _ in points) - min(x for x, _ in points), 2),
        round(max(y for _, y in points) - min(y for _, y in points), 2),
    ]
    segments = len(top_level_blocks(text, "segment"))
    track_arcs = len(top_level_blocks(text, "arc"))
    vias = len(top_level_blocks(text, "via"))
    return {
        "outline_mm": outline,
        "edge_cuts_sha256": hashlib.sha256("\n".join(sorted(edge_blocks)).encode()).hexdigest(),
        "footprints": len(top_level_blocks(text, "footprint")),
        "tracks": segments + track_arcs + vias,
        "zones": len(top_level_blocks(text, "zone")),
    }


def power_region_digest(text: str) -> tuple[str, str]:
    net_names = {
        int(number): name
        for number, name in re.findall(r'^\t\(net (\d+) "([^"]+)"\)', text, re.MULTILINE)
    }
    wanted_nets = {"+BATT", "GND", "Net-(D1-K)", "Net-(U9-SW)", "Net-(U9-BST)"}
    copper_blocks = []
    for keyword in ("segment", "via"):
        for block in top_level_blocks(text, keyword):
            net_match = re.search(r"\(net (\d+)\)", block)
            points = [
                (float(x), float(y))
                for x, y in re.findall(r"\((?:start|end|at) ([^ )]+) ([^ )]+)\)", block)
            ]
            if (
                net_match
                and net_names.get(int(net_match.group(1))) in wanted_nets
                and any(94.0 <= x <= 105.0 and 98.0 <= y <= 106.0 for x, y in points)
            ):
                copper_blocks.append(block)
    if len(copper_blocks) != 55:
        fail(f"unexpected power-region copper inventory: {len(copper_blocks)}")
    payload = "\n".join([
        footprint_block(text, "C45"),
        footprint_block(text, "D1"),
        footprint_block(text, "C22"),
        *sorted(copper_blocks),
    ])
    zones = top_level_blocks(text, "zone")
    if len(zones) != 1:
        fail(f"unexpected filled-zone inventory: {len(zones)}")
    return hashlib.sha256(payload.encode()).hexdigest(), hashlib.sha256(zones[0].encode()).hexdigest()


for path in (
    SCH,
    PCB,
    PRO,
    COMMITTED_NETLIST,
    BASE_NETLIST,
    BASE_DRC,
    COMMITTED_PORT_DRC,
    BASE_ERC,
    COMMITTED_PORT_ERC,
    SUMMARY,
):
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(REPO)}")

for path, expected_hash in BASELINE_SHA256.items():
    if sha256(path) != expected_hash:
        fail(f"pinned upstream baseline changed: {path.relative_to(REPO)}")

project = load_json(PRO)
if canonical_sha256(project_policy(project)) != PROJECT_POLICY_SHA256:
    fail("ERC/DRC rule, constraint, or exclusion policy changed")

board_files = list(ROOT.glob("*.kicad_pcb"))
if board_files != [PCB]:
    fail(f"strict port must contain exactly one active PCB: {board_files}")
if any(ROOT.glob("*daughterboard*")):
    fail("daughterboard artifact exists in the active strict-port branch")

sch_text = SCH.read_text(encoding="utf-8")
pcb_text = PCB.read_text(encoding="utf-8")
main_text = (ROOT / "main.kicad_sch").read_text(encoding="utf-8")
power_text = (ROOT / "power.kicad_sch").read_text(encoding="utf-8")
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

j4_footprint = footprint_block(pcb_text, "J4")
j4_symbol = symbol_block(main_text, "J4")
j4_footprint_uuid_match = re.search(r'\n\t\t\(uuid "([^"]+)"\)', j4_footprint)
if not j4_footprint_uuid_match:
    fail("J4 footprint UUID missing")
j4_footprint_uuid = j4_footprint_uuid_match.group(1)
j4_geometry_digest, j4_pad_uuids = j4_pad_geometry(j4_footprint)
if j4_geometry_digest != J4_FOOTPRINT_SHA256:
    fail("J4 footprint differs from the qualified DRC-clean candidate")
power_digest, filled_zone_digest = power_region_digest(pcb_text)
if power_digest != POWER_REGION_SHA256:
    fail("power-stage footprint or local copper geometry changed")
if filled_zone_digest != FILLED_ZONE_SHA256:
    fail("filled copper zone changed or is stale")
j4_manufacturing_identity = {
    "Datasheet": "https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets/REF-182665-01",
    "Field4": "Toby Electronics",
    "Field5": "REF-182665-01",
    "Field6": "REF-182665-01",
    "Field7": "Toby Electronics",
    "Field8": "REF-182665-01",
    "Manufacturer_Name": "Toby Electronics",
    "Manufacturer_Part_Number": "REF-182665-01",
    "LCSC Part": "",
}
for field, expected in j4_manufacturing_identity.items():
    if property_value(j4_symbol, field) != expected or property_value(j4_footprint, field) != expected:
        fail(f"J4 manufacturing identity changed: {field}")

output_capacitor_identity = {
    "Value": "22u 10V",
    "Man. Ref.": "GRM188R61A226ME15D",
    "LCSC Part": "C84419",
}
for ref in ("C21", "C22"):
    capacitor_symbol = symbol_block(power_text, ref)
    capacitor_footprint = footprint_block(pcb_text, ref)
    for field, expected in output_capacitor_identity.items():
        if property_value(capacitor_symbol, field) != expected or property_value(capacitor_footprint, field) != expected:
            fail(f"{ref} output-capacitor identity changed: {field}")
    if property_value(capacitor_symbol, "Footprint") != "Capacitor_SMD:C_0603_1608Metric" or not capacitor_footprint.lstrip().startswith('(footprint "Capacitor_SMD:C_0603_1608Metric"'):
        fail(f"{ref} output-capacitor footprint changed")

c45_symbol = symbol_block(power_text, "C45")
c45_footprint = footprint_block(pcb_text, "C45")
c45_symbol_uuid_match = re.search(r'\n\t\t\(uuid "([^"]+)"\)', c45_symbol)
if not c45_symbol_uuid_match:
    fail("C45 symbol UUID missing")
c45_symbol_uuid = c45_symbol_uuid_match.group(1)
c45_identity = {
    "Value": "10uF 50V X7R",
    "Datasheet": "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER71H106KA12-01.pdf",
    "Description": "10 uF 50 V X7R ceramic capacitor, 1210",
    "Man.": "Murata",
    "Man. Ref.": "GRM32ER71H106KA12L",
    "LCSC Part": "C77102",
    "Dielectric": "X7R",
    "Voltage Rating": "50V",
}
for field, expected in c45_identity.items():
    if property_value(c45_symbol, field) != expected or property_value(c45_footprint, field) != expected:
        fail(f"C45 input-capacitor identity changed: {field}")
if property_value(c45_symbol, "Footprint") != "Capacitor_SMD:C_1210_3225Metric":
    fail("C45 footprint assignment changed")
if '(layer "B.Cu")' not in c45_footprint or '(at 99.05 100.95 90)' not in c45_footprint:
    fail("C45 placement changed")
d1_footprint = footprint_block(pcb_text, "D1")
d1_uuid_match = re.search(r'\n\t\t\(uuid "([^"]+)"\)', d1_footprint)
if not d1_uuid_match:
    fail("D1 footprint UUID missing")
d1_footprint_uuid = d1_uuid_match.group(1)
c22_footprint = footprint_block(pcb_text, "C22")
c22_uuid_match = re.search(r'\n\t\t\(uuid "([^"]+)"\)', c22_footprint)
if not c22_uuid_match:
    fail("C22 footprint UUID missing")
c22_footprint_uuid = c22_uuid_match.group(1)

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
    ("R18", ROOT / "sensors.kicad_sch"),
    ("R19", ROOT / "sensors.kicad_sch"),
    ("R20", ROOT / "sensors.kicad_sch"),
    ("R21", ROOT / "sensors.kicad_sch"),
    ("R34", ROOT / "sensors.kicad_sch"),
    ("R35", ROOT / "sensors.kicad_sch"),
    ("R38", ROOT / "sensors.kicad_sch"),
    ("R39", ROOT / "sensors.kicad_sch"),
):
    if "(dnp yes)" not in symbol_block(source.read_text(encoding="utf-8"), ref):
        fail(f"{ref} must remain DNP")
    pcb_block = footprint_block(pcb_text, ref)
    if "(attr smd dnp)" not in pcb_block and "(attr through_hole dnp)" not in pcb_block:
        fail(f"PCB footprint {ref} must remain DNP")

for ref, source in (
    ("J5", ROOT / "sensors.kicad_sch"),
    ("U8", ROOT / "dynamixel.kicad_sch"),
):
    if "(dnp no)" not in symbol_block(source.read_text(encoding="utf-8"), ref):
        fail(f"{ref} must remain populated in the default assembly")
    if re.search(r"\(attr (?:smd|through_hole) dnp\)", footprint_block(pcb_text, ref)):
        fail(f"PCB footprint {ref} must remain populated in the default assembly")

cli = find_kicad_cli()
require_kicad_version(cli)
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

    baseline_netlist = BASE_NETLIST
    baseline_erc_path = BASE_ERC
    baseline_drc_path = BASE_DRC
    upstream_directory = os.environ.get("UPSTREAM_SOURCE_DIR")
    if upstream_directory:
        upstream = Path(upstream_directory).resolve()
        upstream_sch = upstream / "elec_RPI_Robot_HAT.kicad_sch"
        upstream_pcb = upstream / "elec_RPI_Robot_HAT.kicad_pcb"
        revision = subprocess.run(
            ["git", "-C", str(upstream), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if revision.returncode != 0 or revision.stdout.strip() != UPSTREAM_COMMIT:
            fail("UPSTREAM_SOURCE_DIR is not the pinned upstream commit")
        dirty = subprocess.run(
            ["git", "-C", str(upstream), "status", "--porcelain"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if dirty.returncode != 0 or dirty.stdout.strip():
            fail("UPSTREAM_SOURCE_DIR must be a clean pinned checkout")
        baseline_netlist = temporary / "upstream_netlist.xml"
        baseline_erc_path = temporary / "upstream_erc.json"
        baseline_drc_path = temporary / "upstream_drc.json"
        run_kicad(cli, ["sch", "erc", "--format", "json", "--severity-all", "-o", str(baseline_erc_path), str(upstream_sch)])
        run_kicad(cli, ["sch", "export", "netlist", "--format", "kicadxml", "-o", str(baseline_netlist), str(upstream_sch)])
        run_kicad(cli, ["pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", str(baseline_drc_path), str(upstream_pcb)])

    if netlist_signature(fresh_netlist_path) != netlist_signature(COMMITTED_NETLIST):
        fail("committed Radxa netlist is stale relative to the current schematic")
    validate_upstream_netlist(baseline_netlist, fresh_netlist_path)

    fresh_root = ET.parse(fresh_netlist_path).getroot()
    components = fresh_root.findall("./components/comp")
    nets = fresh_root.findall("./nets/net")
    if len(components) != 129 or len(nets) != 95:
        fail(f"unexpected netlist size: {len(components)} components / {len(nets)} nets")

    expected_header = {
        1: "+3V3",
        2: "+5V",
        3: "I2C3_SDA_M0",
        4: "+5V",
        5: "I2C3_SCL_M0",
        6: "GND",
        7: "GPIO3_C4_P7",
        8: "UART2_TX_M0",
        9: "GND",
        10: "UART2_RX_M0",
        11: "unconnected-(J4-Pin_11-Pad11)",
        12: "I2S3_SCLK_M0",
        13: "unconnected-(J4-Pin_13-Pad13)",
        14: "GND",
        15: "GPIO3_B0_P15",
        16: "unconnected-(J4-Pin_16-Pad16)",
        17: "+3V3",
        18: "unconnected-(J4-Pin_18-Pad18)",
        19: "GPIO4_C3_P19",
        20: "GND",
        21: "GPIO4_C5_P21",
        22: "unconnected-(J4-Pin_22-Pad22)",
        23: "GPIO4_C2_P23",
        24: "GPIO4_C6_P24",
        25: "GND",
        26: "unconnected-(J4-Pin_26-Pad26)",
        27: "I2C4_SDA_M0_P27",
        28: "I2C4_SCL_M0_P28",
        29: "GPIO3_B3_P29",
        30: "GND",
        31: "GPIO3_B4_P31",
        32: "unconnected-(J4-Pin_32-Pad32)",
        33: "unconnected-(J4-Pin_33-Pad33)",
        34: "GND",
        35: "I2S3_LRCK_M0",
        36: "unconnected-(J4-Pin_36-Pad36)",
        37: "unconnected-(J4-Pin_37-Pad37)",
        38: "I2S3_SDI_M0",
        39: "GND",
        40: "I2S3_SDO_M0",
    }
    actual_header = {}
    for net in nets:
        for node in net.findall("node"):
            pin = node.get("pin", "")
            if node.get("ref") == "J4" and pin.isdigit():
                actual_header[int(pin)] = net.get("name", "").rsplit("/", 1)[-1]
    if actual_header != expected_header:
        fail(f"J4 mapping mismatch: {actual_header}")

    base_drc = load_json(baseline_drc_path)
    committed_drc = load_json(COMMITTED_PORT_DRC)
    fresh_drc = load_json(fresh_drc_path)
    validate_report_contract(base_drc, kind="drc", source="elec_RPI_Robot_HAT.kicad_pcb", ignored=EXPECTED_DRC_IGNORES)
    validate_report_contract(committed_drc, kind="drc", source=PCB.name, ignored=EXPECTED_DRC_IGNORES)
    validate_report_contract(fresh_drc, kind="drc", source=PCB.name, ignored=EXPECTED_DRC_IGNORES)
    base_drc_rows = base_drc.get("violations", [])
    resolved_j4_clearance = [
        finding
        for finding in base_drc_rows
        if finding.get("type") == "hole_clearance"
        and finding.get("severity") == "error"
        and len(finding.get("items", [])) == 2
        and {item.get("uuid") for item in finding["items"]}.issubset(j4_pad_uuids)
    ]
    if len(resolved_j4_clearance) != 40:
        fail("upstream J4 hole-clearance baseline is not the expected 40 findings")
    fresh_drc_rows = fresh_drc.get("violations", [])
    base_d1_library_warning = [
        finding for finding in base_drc_rows
        if finding.get("type") == "lib_footprint_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") == d1_footprint_uuid
    ]
    fresh_d1_library_warning = [
        finding for finding in fresh_drc_rows
        if finding.get("type") == "lib_footprint_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") == d1_footprint_uuid
    ]
    if len(base_d1_library_warning) != 1 or len(fresh_d1_library_warning) != 1:
        fail("D1 inherited library-warning identity changed")
    resolved_identities = Counter(finding_identity(row) for row in resolved_j4_clearance + base_d1_library_warning)
    base_drc_findings = finding_counter(base_drc_rows)
    expected_fresh_drc = base_drc_findings - resolved_identities
    expected_fresh_drc += finding_counter(fresh_d1_library_warning)
    fresh_drc_findings = finding_counter(fresh_drc_rows)
    if fresh_drc_findings != expected_fresh_drc:
        fail("fresh DRC findings differ after approved J4 resolution and D1 relocation")
    if finding_counter(committed_drc.get("violations", [])) != fresh_drc_findings:
        fail("committed Radxa DRC report is stale relative to the current PCB")
    if fresh_drc.get("unconnected_items"):
        fail("routed PCB has unconnected items")
    base_unconnected = Counter(item_identity(item) for item in base_drc["unconnected_items"])
    fresh_unconnected = Counter(item_identity(item) for item in fresh_drc["unconnected_items"])
    committed_unconnected = Counter(item_identity(item) for item in committed_drc["unconnected_items"])
    if fresh_unconnected != base_unconnected:
        fail("fresh unconnected items differ from the upstream baseline")
    if committed_unconnected != fresh_unconnected:
        fail("committed DRC unconnected items are stale")

    base_parity_rows = base_drc.get("schematic_parity", [])
    resolved_j4_parity = [
        finding
        for finding in base_parity_rows
        if finding.get("type") == "footprint_symbol_field_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") == j4_footprint_uuid
    ]
    if len(resolved_j4_parity) != 1:
        fail("pinned upstream J4 parity-resolution set changed")
    fresh_parity_rows = fresh_drc.get("schematic_parity", [])
    moved_footprint_uuids = {c22_footprint_uuid}
    base_moved_parity = [
        finding for finding in base_parity_rows
        if finding.get("type") == "footprint_symbol_field_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") in moved_footprint_uuids
    ]
    fresh_moved_parity = [
        finding for finding in fresh_parity_rows
        if finding.get("type") == "footprint_symbol_field_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") in moved_footprint_uuids
    ]
    if len(base_moved_parity) != 1 or len(fresh_moved_parity) != 1:
        fail("moved C22 parity-warning identity changed")
    expected_port_parity = finding_counter(base_parity_rows)
    expected_port_parity.subtract(finding_counter(resolved_j4_parity + base_moved_parity))
    expected_port_parity += finding_counter(fresh_moved_parity)
    expected_port_parity = +expected_port_parity
    fresh_parity = finding_counter(fresh_parity_rows)
    if fresh_parity != expected_port_parity:
        fail("fresh schematic-parity findings differ after approved J4 metadata correction and power-component relocation")
    if finding_counter(committed_drc.get("schematic_parity", [])) != fresh_parity:
        fail("committed schematic-parity report is stale relative to the current design")

    base_erc = load_json(baseline_erc_path)
    committed_erc = load_json(COMMITTED_PORT_ERC)
    fresh_erc = load_json(fresh_erc_path)
    validate_report_contract(base_erc, kind="erc", source="elec_RPI_Robot_HAT.kicad_sch", ignored=EXPECTED_ERC_IGNORES)
    validate_report_contract(committed_erc, kind="erc", source=SCH.name, ignored=EXPECTED_ERC_IGNORES)
    validate_report_contract(fresh_erc, kind="erc", source=SCH.name, ignored=EXPECTED_ERC_IGNORES)
    base_erc_rows = erc_findings(base_erc)
    fresh_erc_rows = erc_findings(fresh_erc)
    approved_c45_erc = [
        finding
        for finding in fresh_erc_rows
        if finding.get("type") == "lib_symbol_mismatch"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") == c45_symbol_uuid
    ]
    if len(approved_c45_erc) != 1:
        fail("expected exactly one C45 library-symbol warning")
    expected_erc_findings = finding_counter(base_erc_rows) + finding_counter(approved_c45_erc)
    fresh_erc_findings = finding_counter(fresh_erc_rows)
    if fresh_erc_findings != expected_erc_findings:
        fail("fresh ERC findings differ from the normalized upstream baseline plus approved C45 warning")
    if finding_counter(erc_findings(committed_erc)) != fresh_erc_findings:
        fail("committed Radxa ERC report is stale relative to the current schematic")

summary = load_json(SUMMARY)
current_board = board_metrics(pcb_text)
if current_board["edge_cuts_sha256"] != EDGE_CUTS_SHA256:
    fail("Edge.Cuts geometry differs from the pinned upstream outline")
expected_policy_summary = {
    "kicad_version": KICAD_VERSION,
    "erc_ignored_checks": sorted(EXPECTED_ERC_IGNORES),
    "drc_ignored_checks": sorted(EXPECTED_DRC_IGNORES),
    "baseline_regenerated_from_upstream_commit": True,
}
if summary.get("validation_policy") != expected_policy_summary:
    fail("summary validation policy is incomplete or stale")
expected_dnp = ["U4", "J6", "J7", "J8", "R18", "R19", "R20", "R21", "R34", "R35", "R38", "R39"]
if summary.get("dnp_auxiliary_options") != expected_dnp:
    fail("summary auxiliary DNP policy is incomplete or stale")

fresh_erc_rows = erc_findings(fresh_erc)
fresh_drc_rows = fresh_drc["violations"]
fresh_parity_rows = fresh_drc["schematic_parity"]
if summary["erc_baseline"]["types"] != type_counts(fresh_erc_rows):
    fail("summary ERC type counts are stale")
if summary["drc_baseline"].get("resolved_vs_upstream") != len(resolved_j4_clearance):
    fail("summary resolved DRC count is stale")
if summary["drc_baseline"]["types"] != type_counts(fresh_drc_rows):
    fail("summary DRC type counts are stale")
if summary["schematic_parity_baseline"].get("resolved_vs_upstream") != len(resolved_j4_parity):
    fail("summary resolved parity count is stale")
if summary["schematic_parity_baseline"]["types"] != type_counts(fresh_parity_rows):
    fail("summary parity type counts are stale")
if summary["erc_baseline"]["warning"] != severity_counts(fresh_erc_rows)["warning"]:
    fail("summary ERC severity counts are stale")
if summary["drc_baseline"]["error"] != severity_counts(fresh_drc_rows)["error"] or summary["drc_baseline"]["warning"] != severity_counts(fresh_drc_rows)["warning"]:
    fail("summary DRC severity counts are stale")
if summary["schematic_parity_baseline"]["warning"] != severity_counts(fresh_parity_rows)["warning"]:
    fail("summary parity severity counts are stale")
if summary["pcb"]["unconnected_items"] != len(fresh_drc["unconnected_items"]):
    fail("summary unconnected-item count is stale")
expected_summary = {
    "board_count": 1,
    "outline_mm": [65.0, 30.9],
    "footprints": 128,
    "tracks": 1013,
    "erc_total": 56,
    "erc_new": 1,
    "erc_approved": 1,
    "drc_total": 9,
    "drc_new": 0,
    "drc_resolved": 40,
    "parity_total": 110,
    "parity_new": 0,
    "parity_resolved": 1,
}
actual_summary = {
    "board_count": len(board_files),
    "outline_mm": current_board["outline_mm"],
    "footprints": current_board["footprints"],
    "tracks": current_board["tracks"],
    "erc_total": summary["erc_baseline"]["total"],
    "erc_new": summary["erc_baseline"]["new_vs_upstream"],
    "erc_approved": summary["erc_baseline"].get("approved_additions_vs_upstream"),
    "drc_total": summary["drc_baseline"]["total"],
    "drc_new": summary["drc_baseline"]["new_vs_upstream"],
    "drc_resolved": summary["drc_baseline"].get("resolved_vs_upstream"),
    "parity_total": summary["schematic_parity_baseline"]["total"],
    "parity_new": summary["schematic_parity_baseline"]["new_vs_upstream"],
    "parity_resolved": summary["schematic_parity_baseline"].get("resolved_vs_upstream"),
}
if actual_summary != expected_summary or summary.get("fabrication_ready") is not False:
    fail(f"summary mismatch: {actual_summary}")
if current_board["zones"] != summary["pcb"]["zones"]:
    fail(f"summary zone count is stale: current={current_board['zones']}")
if summary["architecture"]["board_count"] != len(board_files):
    fail("summary board count is stale")
if summary["architecture"]["outline_mm"] != current_board["outline_mm"]:
    fail("summary outline is stale")
if summary["pcb"]["footprints"] != current_board["footprints"]:
    fail("summary footprint count is stale")
if summary["pcb"]["tracks"] != current_board["tracks"]:
    fail("summary track count is stale")
expected_host_mapping = {
    str(pin): net
    for pin, net in expected_header.items()
    if net not in {"+3V3", "+5V", "GND"} and not net.startswith("unconnected-")
}
if summary["host_mapping"] != expected_host_mapping:
    fail("summary host mapping is incomplete or stale")

print("STRICT PORT CHECK: PASS")
print(
    "Regenerated KiCad ERC/DRC/parity/netlist evidence and validated one "
    "65.00 x 30.90 mm centerline-outline routed HAT with no new DRC/parity findings "
    "and exactly one approved C45 library-symbol ERC warning versus upstream."
)
