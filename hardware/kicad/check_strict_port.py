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
SUMMARY = REPO / "validation" / "strict_port" / "report_summary.json"
VENDORED_FOOTPRINTS = ROOT / "vendored_footprints_manifest.json"
KICAD_VERSION = "10.0.6"
UPSTREAM_COMMIT = "23eab11927f95ceca0dfa35bf182caeb7db39ea0"
BASELINE_SHA256 = {
    BASE_NETLIST: "210a52c16572f7fcace0787d3f79f60838254019671c4edae41a4ec6a69ede33",
    BASE_ERC: "f50ccd9ea357dbe3f051d5032b9b2796a7255726f048cde3878973ce5e84df44",
    BASE_DRC: "740242aa80c1aa71d9332f64400b382c4a1001b63ab529777bb7625d22cfad18",
}
PROJECT_POLICY_SHA256 = "4adff66c71b09e7c04e35641b1ac3bcad518250f7eb9362f8f85f625805de698"
EDGE_CUTS_SHA256 = "69787bc712e9b43c4ff232a5ceb72b5bce5a73ea0f5e7b6548bc5b64c4cb33bf"
J4_FOOTPRINT_SHA256 = "c0a291611b5e30a0e04bb49e65dced0a51501af583725de1420dad04c8dd1db1"
POWER_REGION_SHA256 = "2f1e45f5384c540af41b758fa840bc456297d2d848594cdb04fde4d87418826b"
FILLED_ZONE_SHA256 = "2bc6aafd6fdacda83edd15b80fea1cfb9daba9127781ba1794de99af1fec9071"
VENDORED_MANIFEST_SHA256 = "030a0768e4b7e3fe0b21237b33c28936e92cb2d2d9051115de3531d4b0bbd430"
STACKUP_SHA256 = "a4b0affb9de794daff5e090fa4778559bac95a151b8528a11fcdac733e54fdae"
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
    "Q3": ("BC847B", "Package_TO_SOT_SMD:SOT-23"),
    "Q4": ("BC847B", "Package_TO_SOT_SMD:SOT-23"),
    "Q5": ("BC847B", "Package_TO_SOT_SMD:SOT-23"),
    "R42": ("100k", "Resistor_SMD:R_0402_1005Metric"),
    "R43": ("10k", "Resistor_SMD:R_0402_1005Metric"),
    "R44": ("10k", "Resistor_SMD:R_0402_1005Metric"),
    "R45": ("10k", "Resistor_SMD:R_0402_1005Metric"),
    "R46": ("100k", "Resistor_SMD:R_0402_1005Metric"),
}
ALLOWED_REMOVED_COMPONENTS = {"H2", "H3", "D2"}  # D2 raw-input clamp replaced by Q3 presence detector.
ALLOWED_COMPONENT_VALUES = {
    "R24": ("10k", "100k"),
    "R3": ("0R", "10k"),
    "C21": ("22u 6V3", "22u 10V"),
    "C22": ("22u 6V3", "22u 10V"),
    "C39": ("100n 6V3", "100nF 50V X7R"),
    "J4": ("Female Header 2x20 SMD", "Radxa ZERO 3W 2x20 HAT Header"),
}
# Stage 1 is a bounded correction, not a new power architecture. See
# validation/strict_port/stage1_power_integrity.json and stage1_copper_changes.json.
STAGE1_IDENTITIES = {
    "Q2": {"Value": "DMN3023L-7", "Manufacturer_Name": "Diodes Incorporated", "Manufacturer_Part_Number": "DMN3023L-7", "LCSC Part": "C443825"},
    "C39": {"Value": "100nF 50V X7R", "Manufacturer_Name": "Samsung Electro-Mechanics", "Manufacturer_Part_Number": "CL05B104KB5NNNC", "LCSC Part": ""},
}
STAGE1_FOOTPRINT_SHA256 = {
    "Q2": "d3fc3276d123ac9d182749480bf9f0b15463d2579a0ddf40e8dff68ffd3ea5bb",
    "R8": "91ed2585a3b1a0c4384eb5f1d64d88fde66b603960f0d1dfbcbd6baf67f3b401",
    "C39": "71edbd4e0577683213d5eb92c0a10397ccb6187659cf336e1d6a33eed6fdfcd3",
}
STAGE1_RESOLVED_PARITY_UUIDS = {"3db277dc-0bd3-4353-9cb2-ed3931b86bb7", "2080a52e-68dc-45dd-a1ce-a708fbf3f890"}
REMOVED_LOGO_SYMBOL_UUIDS = {
    "e8f2ab0f-6624-45f8-b8e5-c599d24045f9",  # H2, Hugging Face
    "27295418-94b8-4760-ba2d-314b58e4124d",  # H3, Pollen Robotics
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


def validate_vendored_footprints() -> None:
    if sha256(VENDORED_FOOTPRINTS) != VENDORED_MANIFEST_SHA256:
        fail("vendored-footprint manifest changed")
    manifest = load_json(VENDORED_FOOTPRINTS)
    expected_libraries = {
        "Library_Pollen": "${KIPRJMOD}/Library_Pollen.pretty",
        "LCSC_parts_lib": "${KIPRJMOD}/LCSC_parts_lib.pretty",
        "Package_TO_SOT_SMD": "${KIPRJMOD}/Package_TO_SOT_SMD.pretty",
    }
    if manifest.get("schema_version") != 1 or manifest.get("kicad_version") != KICAD_VERSION:
        fail("vendored-footprint manifest schema or KiCad version changed")
    if manifest.get("libraries") != expected_libraries:
        fail("vendored-footprint library mapping changed")
    table = ROOT / "fp-lib-table"
    if manifest.get("fp_lib_table_sha256") != sha256(table):
        fail("fp-lib-table changed")
    manifest_files = {entry.get("path"): entry.get("sha256") for entry in manifest.get("files", [])}
    disk_files = {path.relative_to(ROOT).as_posix() for path in ROOT.glob("*.pretty/*.kicad_mod")}
    if len(manifest_files) != 13 or set(manifest_files) != disk_files:
        fail("vendored-footprint file inventory changed")
    for relative, expected_hash in manifest_files.items():
        if sha256(ROOT / relative) != expected_hash:
            fail(f"vendored footprint changed: {relative}")
    if manifest.get("expected_drc_violations") != 0 or manifest.get("expected_erc_footprint_link_issues") != 0:
        fail("vendored-footprint expected finding counts changed")


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


def validate_stage1_power(power_text: str, pcb_text: str, netlist: Path) -> None:
    """Pin exact purchasing identities, enhancement symbol, pads, and VS topology."""
    for ref, expected in STAGE1_IDENTITIES.items():
        symbol = symbol_block(power_text, ref)
        for key, value in expected.items():
            if property_value(symbol, key) != value:
                fail(f"Stage 1 {ref} schematic {key} identity changed")
    q2 = symbol_block(power_text, "Q2")
    if '(lib_id "Transistor_FET:Q_NMOS_GSD")' not in q2:
        fail("Stage 1 Q2 must use the pin-preserving enhancement-mode symbol")
    if property_value(q2, "Footprint") != "Package_TO_SOT_SMD:DMN3023L_SOT23_Diodes":
        fail("Stage 1 Q2 manufacturer land identity changed")
    c39 = symbol_block(power_text, "C39")
    for key, value in {"Man.": "Samsung Electro-Mechanics", "Man. Ref.": "CL05B104KB5NNNC", "Voltage Rating": "50V", "Dielectric": "X7R", "Tolerance": "10%"}.items():
        if property_value(c39, key) != value:
            fail(f"Stage 1 C39 {key} changed")
    if ("7s/25c" in power_text or '(text "24V"' in power_text or '(text "5A"' in power_text
            or "assumed max 8.4V" not in power_text or "Assumed minimum 6.0V" not in power_text):
        fail("Stage 1 battery envelope annotation is missing or stale")
    for ref, expected_hash in STAGE1_FOOTPRINT_SHA256.items():
        if hashlib.sha256(footprint_block(pcb_text, ref).encode()).hexdigest() != expected_hash:
            fail(f"Stage 1 {ref} PCB identity, land, placement, or net changed")
    root = ET.parse(netlist).getroot()
    components = {c.get("ref"): c for c in root.findall("./components/comp")}
    for ref, expected in STAGE1_IDENTITIES.items():
        fields = {f.get("name"): f.text or "" for f in components[ref].findall("./fields/field")}
        fields["Value"] = components[ref].findtext("value")
        if any(fields.get(key) != value for key, value in expected.items()):
            fail(f"Stage 1 {ref} regenerated netlist purchasing identity changed")
    pins = {(node.get("ref"), node.get("pin")): net.get("name")
            for net in root.findall("./nets/net") for node in net.findall("node")}
    expected_pins = {("R8", "1"): "+BATT", ("R8", "2"): "Net-(U10-VS)",
                     ("C39", "1"): "Net-(U10-VS)", ("C39", "2"): "GND",
                     ("U10", "1"): "Net-(U10-VS)", ("U10", "4"): "Net-(D1-K)",
                     ("U10", "5"): "Net-(Q2-G)", ("U10", "6"): "+5V",
                     ("Q2", "1"): "Net-(Q2-G)", ("Q2", "2"): "Net-(D1-K)", ("Q2", "3"): "+5V"}
    for pin, net in expected_pins.items():
        if pins.get(pin) != net:
            fail(f"Stage 1 {pin[0]}.{pin[1]} must connect to {net}")


def stage2_resolved_parity(rows: list[dict]) -> list[dict]:
    # Exact upstream warning identities: removed D2, corrected R24/R3 metadata.
    expected = {
        ("footprint_symbol_field_mismatch", "warning", (("3d68585d-29b4-4ee8-99b5-7155bc8ceb6b", 99.597501, 93.440001),)),
        ("footprint_symbol_field_mismatch", "warning", (("e85025b8-aa89-4d7b-96d2-2a882e5a3148", 98.007501, 97.340001),)),
        ("footprint_symbol_field_mismatch", "warning", (("da1e2968-3898-46d3-8f09-49f562ec5242", 114.897501, 100.540001),)),
    }
    selected = [row for row in rows if finding_identity(row) in expected]
    if finding_counter(selected) != Counter({identity: 1 for identity in expected}):
        fail("Stage 2 D2/R24/R3 exact parity-resolution set changed")
    return selected


def stage2_identities() -> dict:
    values = {"Q3": "BC847B", "Q4": "BC847B", "Q5": "BC847B", "R24": "100k", "R42": "100k", "R46": "100k", "R3": "10k", "R43": "10k", "R44": "10k", "R45": "10k"}
    return {ref: {"Value": value,
                  "Footprint": "Package_TO_SOT_SMD:SOT-23" if ref.startswith("Q") else "Resistor_SMD:R_0402_1005Metric",
                  "Manufacturer_Name": "Nexperia" if ref.startswith("Q") else "Yageo",
                  "Manufacturer_Part_Number": "BC847B,215" if ref.startswith("Q") else ("RC0402FR-07100KL" if value == "100k" else "RC0402FR-0710KL")}
            for ref, value in values.items()}


def validate_stage2_schematics(sheets: dict[str, str]) -> None:
    for ref, expected in stage2_identities().items():
        sheet = "power" if ref in {"Q3", "R24", "R42", "R43"} else "audio"
        block = symbol_block(sheets[sheet], ref)
        for key, value in expected.items():
            if property_value(block, key) != value:
                fail(f"Stage 2 {ref} schematic {key} identity changed")
        if any(flag not in block for flag in ("(dnp no)", "(in_bom yes)", "(on_board yes)")):
            fail(f"Stage 2 {ref} must remain populated, in BOM, and on board")
        if ref.startswith("Q") and '(lib_id "Transistor_BJT:Q_NPN_BEC")' not in block:
            fail(f"Stage 2 {ref} must use NPN BEC pin order")


def validate_stage2_pcb(pcb_text: str) -> None:
    """Purchasing/population guards; routing and land geometry remain separate."""
    for ref, expected in stage2_identities().items():
        block = footprint_block(pcb_text, ref)
        if not block.lstrip().startswith(f'(footprint "{expected["Footprint"]}"'):
            fail(f"Stage 2 {ref} PCB footprint identity changed")
        for key, value in expected.items():
            if key != "Footprint" and property_value(block, key) != value:
                fail(f"Stage 2 {ref} PCB {key} identity changed")
        attr = re.search(r"\(attr ([^)]+)\)", block)
        flags = set(attr.group(1).split()) if attr else set()
        if "smd" not in flags or flags & {"dnp", "exclude_from_bom", "exclude_from_pos_files", "board_only"}:
            fail(f"Stage 2 {ref} PCB must remain populated in BOM and PnP")


def validate_stage2_netlist(netlist: Path) -> None:
    """Exact host-referenced presence detector and high-Z/default-OFF amp topology.

    Q3 inverts battery presence into a 3V3 pull-up, never a raw battery input.
    R46 holds Q5 off at high-Z; R44 then turns Q4 on, clamping AMP_SHDN low.
    This is a connectivity/identity contract, not an analog or boot-time proof.
    """
    root = ET.parse(netlist).getroot()
    components = {c.get("ref"): c for c in root.findall("./components/comp")}
    if len(components) != len(root.findall("./components/comp")):
        fail("Stage 2 duplicate component reference")
    if "D2" in components:
        fail("Stage 2 D2 must be removed, its raw clamp replaced by Q3")
    for ref, expected in stage2_identities().items():
        if ref not in components:
            fail(f"Stage 2 missing {ref}")
        comp = components[ref]
        fields = {f.get("name"): f.text or "" for f in comp.findall("./fields/field")}
        fields.update(Value=comp.findtext("value"), Footprint=comp.findtext("footprint"))
        if any(fields.get(key) != value for key, value in expected.items()):
            fail(f"Stage 2 {ref} netlist purchasing identity changed")
        if any(p.get("name") in {"dnp", "exclude_from_bom", "exclude_from_board"} for p in comp.findall("property")):
            fail(f"Stage 2 {ref} must remain populated in netlist")
        if ref.startswith("Q"):
            lib = comp.find("libsource")
            if lib is None or (lib.get("lib"), lib.get("part")) != ("Transistor_BJT", "Q_NPN_BEC"):
                fail(f"Stage 2 {ref} netlist must use NPN BEC symbol")
    nets = {n.get("name"): n for n in root.findall("./nets/net")}
    if len(nets) != len(root.findall("./nets/net")):
        fail("Stage 2 duplicate net name")
    pins = {}
    for net in nets.values():
        for node in net.findall("node"):
            key = (node.get("ref"), node.get("pin"))
            if key in pins:
                fail(f"Stage 2 duplicate pin {key}")
            pins[key] = net.get("name")
    exact = {
        "BAT_BASE": {("R24", "1"), ("R42", "1"), ("Q3", "1")},
        "/Schematic/Audio/GPIO3_B4_P31": {("Q3", "3"), ("R43", "1"), ("C44", "1"), ("J4", "31")},
        "AMP_SHDN": {("R3", "1"), ("Q4", "3"), ("U1", "12")},
        "AMP_INHIBIT": {("R44", "1"), ("Q4", "1"), ("Q5", "3")},
        "AMP_BASE": {("R45", "1"), ("Q5", "1"), ("R46", "1")},
        "AMP_ENABLE": {("J4", "11"), ("R45", "2")},
    }
    for name, expected in exact.items():
        actual = {pin for pin, net in pins.items() if net == name}
        if actual != expected:
            fail(f"Stage 2 {name} exact membership changed: {sorted(actual)}")
    for ref in stage2_identities():
        expected_pins = {"1", "2", "3"} if ref.startswith("Q") else {"1", "2"}
        actual_pins = {pin for owner, pin in pins if owner == ref}
        if actual_pins != expected_pins:
            fail(f"Stage 2 {ref} exact pin inventory changed")
        for net in nets.values():
            for node in net.findall("node"):
                if node.get("ref") != ref:
                    continue
                pin = node.get("pin")
                function = {"1": "B_1", "2": "E_2", "3": "C_3"}[pin] if ref.startswith("Q") else ""
                kind = "input" if ref.startswith("Q") and pin == "1" else "passive"
                if (node.get("pinfunction", ""), node.get("pintype", "")) != (function, kind):
                    fail(f"Stage 2 {ref}.{pin} electrical pin tuple changed")
    j11 = nets["AMP_ENABLE"].find("node[@ref='J4'][@pin='11']")
    if (j11.get("pinfunction"), j11.get("pintype")) != ("Pin_11_11", "passive"):
        fail("Stage 2 J4.11 must be a connected passive header pin")
    supply = {"+BATT": {("R24", "2")}, "+3V3": {("R43", "2")},
              "+5V": {("R3", "2"), ("R44", "2"), ("R4", "2")},
              "GND": {("Q3", "2"), ("R42", "2"), ("C44", "2"), ("Q4", "2"), ("Q5", "2"), ("R46", "2")}}
    for name, expected in supply.items():
        for pin in expected:
            if pins.get(pin) != name:
                fail(f"Stage 2 {pin[0]}.{pin[1]} must connect to {name}")


def validate_upstream_netlist(base: Path, port: Path) -> None:
    validate_stage2_netlist(port)
    base_components = component_map(base)
    port_components = component_map(port)
    added = set(port_components) - set(base_components)
    removed = set(base_components) - set(port_components)
    if added != set(ALLOWED_ADDED_COMPONENTS) or removed != ALLOWED_REMOVED_COMPONENTS:
        fail(f"component references differ from upstream: added={sorted(added)}, removed={sorted(removed)}")
    for ref, expected_component in ALLOWED_ADDED_COMPONENTS.items():
        if port_components[ref] != expected_component:
            fail(f"added component identity changed: {ref}")
    differences = {
        ref: (base_components[ref], port_components[ref])
        for ref in set(base_components) & set(port_components)
        if base_components[ref] != port_components[ref]
    }
    expected = {
        ref: ((before, base_components[ref][1]), (after, base_components[ref][1]))
        for ref, (before, after) in ALLOWED_COMPONENT_VALUES.items()
    }
    expected["Q2"] = (("SI2312CDS-T1-GE3", "Package_TO_SOT_SMD:TSOT-23"), ("DMN3023L-7", "Package_TO_SOT_SMD:DMN3023L_SOT23_Diodes"))
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
    # Invert only the exact approved R8.1 move; retain its full electrical tuple.
    port_nets = {n.get("name"): n for n in port_root.findall("./nets/net")}
    r8_nodes = [n for n in port_nets["+BATT"].findall("node") if n.get("ref") == "R8" and n.get("pin") == "1"]
    if len(r8_nodes) != 1:
        fail("Stage 1 R8.1 battery bias is missing")
    r8 = tuple(r8_nodes[0].get(k, "") for k in ("ref", "pin", "pinfunction", "pintype"))
    normalized_port_memberships = set()
    for name, net in port_nets.items():
        nodes = [tuple(n.get(k, "") for k in ("ref", "pin", "pinfunction", "pintype")) for n in net.findall("node") if n.get("ref") != "C45"]
        if name == "+BATT":
            nodes.remove(r8)
        if name == "+5V":
            nodes.append(r8)
        # Invert Stage 2 only after its exact topology and all new pin tuples
        # have been checked. Do not discard any other upstream component/pin.
        new_refs = {"Q3", "Q4", "Q5", "R42", "R43", "R44", "R45", "R46"}
        nodes = [node for node in nodes if node[0] not in new_refs]
        if name == "BAT_BASE":
            nodes.remove(("R24", "1", "", "passive"))
        if name == "/Schematic/Audio/GPIO3_B4_P31":
            nodes.extend([("R24", "1", "", "passive"), ("D2", "1", "K_1", "passive")])
        if name == "GND":
            nodes.append(("D2", "2", "A_2", "passive"))
        if name == "AMP_ENABLE":
            nodes.remove(("J4", "11", "Pin_11_11", "passive"))
            nodes.append(("J4", "11", "Pin_11_11", "passive+no_connect"))
        # BAT_BASE/AMP_BASE/AMP_INHIBIT are the only nets removed by inversion.
        if nodes or name not in {"BAT_BASE", "AMP_BASE", "AMP_INHIBIT"}:
            normalized_port_memberships.add(tuple(sorted(nodes)))
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


def stackup_digest(text: str) -> str:
    start = text.find("\n\t\t(stackup")
    if start < 0:
        fail("PCB stackup block missing")
    depth = 0
    end = None
    for index in range(start + 1, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    thickness = re.search(r"\(general\s+\(thickness ([^)]+)\)", text, re.DOTALL)
    if end is None or not thickness:
        fail("PCB stackup or board thickness is malformed")
    payload = thickness.group(1) + "\n" + text[start:end]
    return hashlib.sha256(payload.encode()).hexdigest()


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
    if len(copper_blocks) != 60:
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
    VENDORED_FOOTPRINTS,
    ROOT / "fp-lib-table",
):
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(REPO)}")

for path, expected_hash in BASELINE_SHA256.items():
    if sha256(path) != expected_hash:
        fail(f"pinned upstream baseline changed: {path.relative_to(REPO)}")
validate_vendored_footprints()

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
if stackup_digest(pcb_text) != STACKUP_SHA256:
    fail("PCB 1.0 mm / 2-1-1-2 oz ENIG stackup changed")

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

u4_source = ROOT / "main.kicad_sch"
if "(dnp yes)" not in symbol_block(u4_source.read_text(encoding="utf-8"), "U4"):
    fail("U4 must remain DNP")
u4_footprint = footprint_block(pcb_text, "U4")
if "(attr smd dnp)" not in u4_footprint and "(attr through_hole dnp)" not in u4_footprint:
    fail("PCB footprint U4 must remain DNP")

for ref, source in (
    ("J1", ROOT / "audio.kicad_sch"),
    ("J2", ROOT / "audio.kicad_sch"),
    ("J5", ROOT / "sensors.kicad_sch"),
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
    ("J9", ROOT / "audio.kicad_sch"),
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
    validate_stage2_schematics({"power": power_text, "audio": (ROOT / "audio.kicad_sch").read_text(encoding="utf-8"), "main": main_text})
    validate_stage2_pcb(pcb_text)
    validate_stage2_netlist(fresh_netlist_path)
    validate_stage2_netlist(COMMITTED_NETLIST)
    validate_stage1_power(power_text, pcb_text, fresh_netlist_path)
    validate_stage1_power(power_text, pcb_text, COMMITTED_NETLIST)
    validate_upstream_netlist(baseline_netlist, fresh_netlist_path)

    fresh_root = ET.parse(fresh_netlist_path).getroot()
    components = fresh_root.findall("./components/comp")
    nets = fresh_root.findall("./nets/net")
    if len(components) != 134 or len(nets) != 98:
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
        11: "AMP_ENABLE",
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
    resolved_library_warnings = [
        finding for finding in base_drc_rows
        if finding.get("type") in {"lib_footprint_issues", "lib_footprint_mismatch"}
        and finding.get("severity") == "warning"
    ]
    if len(resolved_library_warnings) != 9:
        fail("upstream library-warning resolution set is not the expected 9 findings")
    resolved_identities = Counter(
        finding_identity(row)
        for row in resolved_j4_clearance + resolved_library_warnings
    )
    base_drc_findings = finding_counter(base_drc_rows)
    expected_fresh_drc = base_drc_findings - resolved_identities
    fresh_drc_findings = finding_counter(fresh_drc_rows)
    if fresh_drc_findings != expected_fresh_drc:
        fail("fresh DRC findings differ after approved J4 and library resolutions")
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
    stage1_resolved_parity = [
        f for f in base_parity_rows
        if f.get("type") == "footprint_symbol_field_mismatch" and f.get("severity") == "warning"
        and len(f.get("items", [])) == 1 and f["items"][0].get("uuid") in STAGE1_RESOLVED_PARITY_UUIDS
    ]
    if len(stage1_resolved_parity) != 2:
        fail("Stage 1 Q2/C39 exact metadata-parity resolution set changed")
    expected_port_parity = finding_counter(base_parity_rows)
    stage2_parity = stage2_resolved_parity(base_parity_rows)
    expected_port_parity.subtract(finding_counter(resolved_j4_parity + base_moved_parity + stage1_resolved_parity + stage2_parity))
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
    resolved_footprint_links = [
        finding for finding in base_erc_rows
        if finding.get("type") == "footprint_link_issues"
        and finding.get("severity") == "warning"
    ]
    if len(resolved_footprint_links) != 8:
        fail("upstream footprint-link resolution set is not the expected 8 findings")
    resolved_logo_symbol_warnings = [
        finding for finding in base_erc_rows
        if finding.get("type") == "lib_symbol_issues"
        and finding.get("severity") == "warning"
        and len(finding.get("items", [])) == 1
        and finding["items"][0].get("uuid") in REMOVED_LOGO_SYMBOL_UUIDS
    ]
    if len(resolved_logo_symbol_warnings) != 2:
        fail("upstream removed-logo ERC resolution set is not the expected 2 findings")
    expected_erc_findings = finding_counter(base_erc_rows)
    expected_erc_findings.subtract(
        finding_counter(resolved_footprint_links + resolved_logo_symbol_warnings)
    )
    expected_erc_findings = +expected_erc_findings
    expected_erc_findings += finding_counter(approved_c45_erc)
    fresh_erc_findings = finding_counter(fresh_erc_rows)
    if fresh_erc_findings != expected_erc_findings:
        fail("fresh ERC findings differ after approved footprint-link resolutions and C45 warning")
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
expected_dnp_options = ["C25", "R10", "R11", "R16", "R17", "R36", "R37", "R41", "U4"]
if summary.get("dnp_options") != expected_dnp_options:
    fail("summary DNP policy is incomplete or stale")
expected_qwiic_population = [
    "J5", "J6", "J7", "J8", "R18", "R19", "R20", "R21", "R34", "R35", "R38", "R39",
]
if summary.get("qwiic_functional_parity", {}).get("populated") != expected_qwiic_population:
    fail("summary Qwiic population policy is incomplete or stale")
if summary.get("qwiic_functional_parity", {}).get("overlay") != "software/overlays/radxa-zero3w-robot-hat-qwiic.dts":
    fail("summary Qwiic overlay policy is incomplete or stale")

fresh_erc_rows = erc_findings(fresh_erc)
fresh_drc_rows = fresh_drc["violations"]
fresh_parity_rows = fresh_drc["schematic_parity"]
if summary["erc_baseline"]["types"] != type_counts(fresh_erc_rows):
    fail("summary ERC type counts are stale")
if summary["erc_baseline"].get("resolved_vs_upstream") != len(resolved_footprint_links) + len(resolved_logo_symbol_warnings):
    fail("summary resolved ERC count is stale")
if summary["drc_baseline"].get("resolved_vs_upstream") != len(resolved_j4_clearance) + len(resolved_library_warnings):
    fail("summary resolved DRC count is stale")
if summary["drc_baseline"]["types"] != type_counts(fresh_drc_rows):
    fail("summary DRC type counts are stale")
if summary["schematic_parity_baseline"].get("resolved_vs_upstream") != len(resolved_j4_parity) + len(stage1_resolved_parity) + len(stage2_parity):
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
    "footprints": 133,
    "tracks": 1396,
    "erc_total": 46,
    "erc_new": 1,
    "erc_approved": 1,
    "erc_resolved": 10,
    "drc_total": 0,
    "drc_new": 0,
    "drc_resolved": 49,
    "parity_total": 105,
    "parity_new": 0,
    "parity_resolved": 6,
}
actual_summary = {
    "board_count": len(board_files),
    "outline_mm": current_board["outline_mm"],
    "footprints": current_board["footprints"],
    "tracks": current_board["tracks"],
    "erc_total": summary["erc_baseline"]["total"],
    "erc_new": summary["erc_baseline"]["new_vs_upstream"],
    "erc_approved": summary["erc_baseline"].get("approved_additions_vs_upstream"),
    "erc_resolved": summary["erc_baseline"].get("resolved_vs_upstream"),
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
expected_manufacturing_stackup = {
    "copper_layers": 4,
    "thickness_mm": 1.0,
    "copper_um": [70, 35, 35, 70],
    "surface_finish": "ENIG",
}
if any(summary["architecture"].get(key) != value for key, value in expected_manufacturing_stackup.items()):
    fail("summary manufacturing stackup is stale")
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
    "65.00 x 30.90 mm centerline-outline routed HAT with zero DRC findings, "
    "ten resolved ERC warnings including the removed H2/H3 logo symbols, and "
    "exactly one approved C45 library-symbol ERC warning versus upstream."
)
