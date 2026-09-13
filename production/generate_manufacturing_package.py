#!/usr/bin/env python3
"""Generate and validate a non-approved manufacturing release candidate."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

REPO = Path(__file__).resolve().parents[1]
PCB = REPO / "hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb"
SCH = REPO / "hardware/kicad/radxa_zero3w_robot_hat.kicad_sch"
PRODUCTION = REPO / "production"
RELEASES = PRODUCTION / "releases"
KICAD_VERSION = "10.0.6"
DNP = {
    "C25", "R10", "R11", "R16", "R17", "R36", "R37", "R41", "U4",
}
REQUIRED_POPULATED = {
    "C45", "J1", "J2", "J5", "J6", "J7", "J8", "J9", "R18", "R19", "R20", "R21",
    "R34", "R35", "R38", "R39", "U8",
}
GERBER_LAYERS = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu", "F.Paste", "B.Paste", "F.Silkscreen", "B.Silkscreen", "F.Mask", "B.Mask", "Edge.Cuts"]
BOARD_NAME = PCB.stem
GERBER_PATHS = {
    f"gerber/{BOARD_NAME}-F_Cu.gtl",
    f"gerber/{BOARD_NAME}-In1_Cu.g1",
    f"gerber/{BOARD_NAME}-In2_Cu.g2",
    f"gerber/{BOARD_NAME}-B_Cu.gbl",
    f"gerber/{BOARD_NAME}-F_Paste.gtp",
    f"gerber/{BOARD_NAME}-B_Paste.gbp",
    f"gerber/{BOARD_NAME}-F_Silkscreen.gto",
    f"gerber/{BOARD_NAME}-B_Silkscreen.gbo",
    f"gerber/{BOARD_NAME}-F_Mask.gts",
    f"gerber/{BOARD_NAME}-B_Mask.gbs",
    f"gerber/{BOARD_NAME}-Edge_Cuts.gm1",
    f"gerber/{BOARD_NAME}-job.gbrjob",
}
DRILL_PATHS = {
    f"drill/{BOARD_NAME}-PTH.drl",
    f"drill/{BOARD_NAME}-NPTH.drl",
    f"drill/{BOARD_NAME}-PTH-drl_map.pdf",
    f"drill/{BOARD_NAME}-NPTH-drl_map.pdf",
    "drill/drill_report.txt",
}
EXPECTED_ARCHIVE_PATHS = GERBER_PATHS | DRILL_PATHS
EXPECTED_EXPORT_PATHS = EXPECTED_ARCHIVE_PATHS | {
    "bom/bom_full.csv",
    "bom/bom_populated.csv",
    "pnp/positions_all.csv",
    "pnp/positions_populated.csv",
    "assembly/assembly_top.pdf",
    "assembly/assembly_bottom.pdf",
    "assembly/schematic.pdf",
}
EXPECTED_PACKAGE_PATHS = EXPECTED_EXPORT_PATHS | {"README.md", "fabrication_gerber_drill.zip", "manifest.json"}
GERBER_FILENAMES = {Path(path).name for path in GERBER_PATHS if not path.endswith(".gbrjob")}
DRILL_FILENAMES = {f"{BOARD_NAME}-PTH.drl", f"{BOARD_NAME}-NPTH.drl"}
PDF_FILENAMES = {
    f"{BOARD_NAME}-PTH-drl_map.pdf",
    f"{BOARD_NAME}-NPTH-drl_map.pdf",
    "assembly_top.pdf",
    "assembly_bottom.pdf",
    "schematic.pdf",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str) -> None:
    result = subprocess.run(args, cwd=REPO, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stdout}\n{result.stderr}")


def find_kicad() -> str:
    configured = os.environ.get("KICAD_CLI")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    found = shutil.which("kicad-cli")
    if found:
        candidates.append(Path(found))
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(os.environ["LOCALAPPDATA"]) / "Programs/KiCad/10.0/bin/kicad-cli.exe")
    for path in candidates:
        if path.is_file():
            result = subprocess.run([str(path), "--version"], text=True, capture_output=True, encoding="utf-8", errors="replace")
            if result.returncode == 0 and result.stdout.strip() == KICAD_VERSION:
                return str(path)
    raise SystemExit(f"KiCad {KICAD_VERSION} CLI not found")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def refs(rows: list[dict[str, str]], key: str) -> set[str]:
    result = set()
    for row in rows:
        result.update(item for item in re.split(r"[, ]+", row.get(key, "").strip()) if item)
    return result


def validated_output_path(output: Path, releases: Path = RELEASES) -> Path:
    resolved = output.resolve()
    try:
        relative_output = resolved.relative_to(releases.resolve())
    except ValueError:
        raise SystemExit("output must be inside the repository production/releases directory")
    if not relative_output.parts:
        raise SystemExit("output must be a child directory of production/releases")
    return resolved


def replace_metadata(data: bytes, pattern: bytes, replacement: bytes, label: str) -> bytes:
    normalized, count = re.subn(pattern, replacement, data, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"unexpected {label} metadata inventory")
    if len(normalized) != len(data):
        raise SystemExit(f"{label} metadata normalization changed file length")
    return normalized


def normalized_kicad_bytes(data: bytes, source_epoch: int, filename: str) -> bytes:
    timestamp = datetime.fromtimestamp(source_epoch, tz=timezone.utc)
    iso_tz = timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00").encode()
    iso = timestamp.strftime("%Y-%m-%dT%H:%M:%S").encode()
    spaced = timestamp.strftime("%Y-%m-%d %H:%M:%S").encode()
    pdf = timestamp.strftime("%Y:%m:%d:%H:%M:%S").encode()
    if filename in GERBER_FILENAMES:
        data = replace_metadata(data, rb"^(%TF\.CreationDate,)20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d(\*%\r?)$", rb"\g<1>" + iso_tz + rb"\g<2>", "Gerber CreationDate")
        data = replace_metadata(data, rb"^(G04 Created by KiCad \(PCBNEW 10\.0\.6\) date )20\d\d-\d\d-\d\d \d\d:\d\d:\d\d(\*\r?)$", rb"\g<1>" + spaced + rb"\g<2>", "Gerber comment date")
    elif filename == f"{BOARD_NAME}-job.gbrjob":
        data = replace_metadata(data, rb'^([ \t]*"CreationDate": ")20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d("\r?)$', rb"\g<1>" + iso_tz + rb"\g<2>", "Gerber job CreationDate")
    elif filename in DRILL_FILENAMES:
        data = replace_metadata(data, rb"^(; DRILL file KiCad 10\.0\.6 date )20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\r?)$", rb"\g<1>" + iso + rb"\g<2>", "drill comment date")
        data = replace_metadata(data, rb"^(; #@! TF\.CreationDate,)20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d(\r?)$", rb"\g<1>" + iso_tz + rb"\g<2>", "drill CreationDate")
    elif filename == "drill_report.txt":
        data = replace_metadata(data, rb"^(Created on )20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\r?)$", rb"\g<1>" + iso + rb"\g<2>", "drill report date")
    elif filename in PDF_FILENAMES:
        data = replace_metadata(data, rb"^(/CreationDate \(D:)20\d\d:\d\d:\d\d:\d\d:\d\d:\d\d(\)\r?)$", rb"\g<1>" + pdf + rb"\g<2>", "PDF CreationDate")
    return data


def zip_date_time(source_epoch: int) -> tuple[int, int, int, int, int, int]:
    parts = list(datetime.fromtimestamp(source_epoch, tz=timezone.utc).timetuple()[:6])
    parts[5] -= parts[5] % 2
    return tuple(parts)


def write_deterministic_zip(archive_path: Path, root: Path, paths: list[Path], source_epoch: int) -> None:
    date_time = zip_date_time(source_epoch)
    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in sorted(paths):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), date_time=date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def inventory(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def validate_inventory(root: Path, expected: set[str], label: str) -> None:
    actual = inventory(root)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SystemExit(f"unexpected {label} inventory; missing={missing}, extra={extra}")


def validate_reference_exports(
    full_bom_refs: set[str],
    populated_bom_refs: set[str],
    all_pos_refs: set[str],
    populated_pos_refs: set[str],
    dnp: set[str] = DNP,
) -> None:
    if not populated_bom_refs <= full_bom_refs or full_bom_refs - populated_bom_refs != dnp:
        raise SystemExit("unexpected BOM reference inventory")
    if not populated_pos_refs <= all_pos_refs or all_pos_refs - populated_pos_refs != dnp:
        raise SystemExit("unexpected PnP reference inventory")


def validate_required_populated(
    populated_bom_refs: set[str],
    populated_pos_refs: set[str],
    required: set[str] = REQUIRED_POPULATED,
) -> None:
    missing_bom = sorted(required - populated_bom_refs)
    if missing_bom:
        raise SystemExit(f"required populated references missing from BOM: {missing_bom}")
    missing_pnp = sorted(required - populated_pos_refs)
    if missing_pnp:
        raise SystemExit(f"required populated references missing from PnP: {missing_pnp}")


def validate_zip(archive_path: Path, root: Path, expected_paths: set[str], source_epoch: int) -> None:
    expected_names = sorted(expected_paths)
    expected_date = zip_date_time(source_epoch)
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if [info.filename for info in infos] != expected_names or archive.testzip() is not None:
            raise SystemExit("unexpected fabrication ZIP inventory or CRC")
        for info in infos:
            if info.date_time != expected_date or info.create_system != 3 or info.external_attr != 0o100644 << 16:
                raise SystemExit("unexpected fabrication ZIP metadata")
            if archive.read(info.filename) != (root / info.filename).read_bytes():
                raise SystemExit("fabrication ZIP content differs from source export")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
        raise SystemExit("source commit must be a 7-40 digit lowercase hexadecimal Git object id")
    source_epoch_text = subprocess.check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd=REPO, text=True).strip()
    if not source_epoch_text.isdigit():
        raise SystemExit("source commit timestamp must be a non-negative integer")
    source_epoch = int(source_epoch_text)
    short = commit[:8]
    tracked_status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO, text=True)
    if tracked_status.strip():
        raise SystemExit("tracked working tree must be clean before manufacturing export")

    output = validated_output_path(args.output or (RELEASES / short))
    if output.exists():
        if not args.force:
            raise SystemExit(f"output exists: {output}; use --force to replace it")
        shutil.rmtree(output)
    for name in ("gerber", "drill", "bom", "pnp", "assembly"):
        (output / name).mkdir(parents=True, exist_ok=True)

    kicad = find_kicad()
    run(kicad, "pcb", "export", "gerbers", "--output", str(output / "gerber"), "--layers", ",".join(GERBER_LAYERS), "--precision", "6", "--check-zones", str(PCB))
    run(kicad, "pcb", "export", "drill", "--output", str(output / "drill"), "--format", "excellon", "--drill-origin", "absolute", "--excellon-zeros-format", "decimal", "--excellon-oval-format", "route", "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "pdf", "--generate-report", "--report-path", str(output / "drill/drill_report.txt"), str(PCB))
    run(kicad, "pcb", "export", "pos", "--output", str(output / "pnp/positions_populated.csv"), "--side", "both", "--format", "csv", "--units", "mm", "--smd-only", "--exclude-dnp", str(PCB))
    run(kicad, "pcb", "export", "pos", "--output", str(output / "pnp/positions_all.csv"), "--side", "both", "--format", "csv", "--units", "mm", "--smd-only", str(PCB))
    fields = "Reference,Value,Footprint,QUANTITY,DNP,Man.,Man. Ref.,LCSC Part,Datasheet"
    labels = "Refs,Value,Footprint,Qty,DNP,Manufacturer,Manufacturer Part,LCSC Part,Datasheet"
    run(kicad, "sch", "export", "bom", "--output", str(output / "bom/bom_full.csv"), "--fields", fields, "--labels", labels, "--sort-field", "Reference", str(SCH))
    run(kicad, "sch", "export", "bom", "--output", str(output / "bom/bom_populated.csv"), "--fields", fields, "--labels", labels, "--sort-field", "Reference", "--exclude-dnp", str(SCH))
    run(kicad, "pcb", "export", "pdf", "--output", str(output / "assembly/assembly_top.pdf"), "--mode-single", "--layers", "F.Fab,F.Silkscreen,Edge.Cuts", "--sketch-pads-on-fab-layers", "--crossout-DNP-footprints-on-fab-layers", "--black-and-white", "--check-zones", str(PCB))
    run(kicad, "pcb", "export", "pdf", "--output", str(output / "assembly/assembly_bottom.pdf"), "--mode-single", "--layers", "B.Fab,B.Silkscreen,Edge.Cuts", "--mirror", "--sketch-pads-on-fab-layers", "--crossout-DNP-footprints-on-fab-layers", "--black-and-white", "--check-zones", str(PCB))
    run(kicad, "sch", "export", "pdf", "--output", str(output / "assembly/schematic.pdf"), str(SCH))

    for directory in (output / "gerber", output / "drill", output / "assembly"):
        for path in directory.iterdir():
            if path.is_file():
                path.write_bytes(normalized_kicad_bytes(path.read_bytes(), source_epoch, path.name))

    validate_inventory(output, EXPECTED_EXPORT_PATHS, "export")
    job_path = output / f"gerber/{BOARD_NAME}-job.gbrjob"
    job_files = [entry.get("Path") for entry in json.loads(job_path.read_text(encoding="utf-8"))["FilesAttributes"]]
    expected_job_files = sorted(Path(path).name for path in GERBER_PATHS if not path.endswith(".gbrjob"))
    if len(job_files) != 11 or sorted(job_files) != expected_job_files:
        raise SystemExit("unexpected Gerber job file mapping")
    layers = [output / path for path in GERBER_PATHS if not path.endswith(".gbrjob")]
    if any(path.stat().st_size <= 100 for path in layers):
        raise SystemExit("empty or suspiciously small Gerber layer")

    report = (output / "drill/drill_report.txt").read_text(encoding="utf-8", errors="replace")
    plated = re.search(r"Total plated holes count (\d+)", report)
    unplated = re.search(r"Total unplated holes count (\d+)", report)
    if not plated or not unplated or int(plated.group(1)) != 131 or int(unplated.group(1)) != 42:
        raise SystemExit("unexpected drill counts")

    full_bom = csv_rows(output / "bom/bom_full.csv")
    populated_bom = csv_rows(output / "bom/bom_populated.csv")
    all_pos = csv_rows(output / "pnp/positions_all.csv")
    populated_pos = csv_rows(output / "pnp/positions_populated.csv")
    full_refs = refs(full_bom, "Refs")
    populated_refs = refs(populated_bom, "Refs")
    all_pos_refs = refs(all_pos, "Ref")
    populated_pos_refs = refs(populated_pos, "Ref")
    if (len(full_bom), len(populated_bom)) != (123, 114):
        raise SystemExit("unexpected BOM row counts")
    if (len(all_pos), len(populated_pos)) != (119, 110):
        raise SystemExit("unexpected PnP row counts")
    validate_reference_exports(full_refs, populated_refs, all_pos_refs, populated_pos_refs)
    validate_required_populated(populated_refs, populated_pos_refs)

    pdfs = list((output / "assembly").glob("*.pdf")) + list((output / "drill").glob("*.pdf"))
    if any(not path.read_bytes().startswith(b"%PDF-") for path in pdfs):
        raise SystemExit("invalid PDF output")

    archive_paths = [output / path for path in sorted(EXPECTED_ARCHIVE_PATHS)]
    write_deterministic_zip(output / "fabrication_gerber_drill.zip", output, archive_paths, source_epoch)
    validate_zip(output / "fabrication_gerber_drill.zip", output, EXPECTED_ARCHIVE_PATHS, source_epoch)

    readme = f"""# Manufacturing release candidate {short}\n\n> **NOT ORDER-APPROVED.** `fabrication_ready=false` until the physical and EVT gates in `docs/PROJECT_STATUS.md` are closed.\n\n- Source commit: `{commit}`\n- KiCad: `{KICAD_VERSION}`\n- Board: one 65.00 × 30.90 mm, 4-layer FR-4 PCB\n- Thickness: 1.0 mm\n- Copper: 70/35/35/70 µm (approximately 2/1/1/2 oz)\n- Finish: ENIG\n- Drill: 131 PTH, 42 NPTH\n- Assembly: both sides\n- DNP excluded from populated BOM/PnP: `{', '.join(sorted(DNP))}`\n\nUse `fabrication_gerber_drill.zip` for PCB quotation only. Do not place a production or assembled-board order until the J4, C45 gap, cable, antenna, backfeed, audio-current and thermal gates are signed off.\n"""
    (output / "README.md").write_text(readme, encoding="utf-8", newline="\n")

    manifested_paths = EXPECTED_PACKAGE_PATHS - {"manifest.json"}
    validate_inventory(output, manifested_paths, "pre-manifest package")
    files = [output / path for path in sorted(manifested_paths)]
    manifest = {
        "schema_version": 1,
        "source_commit": commit,
        "kicad_version": KICAD_VERSION,
        "fabrication_ready": False,
        "board": {"count": 1, "outline_mm": [65.0, 30.9], "layers": 4, "thickness_mm": 1.0, "finish": "ENIG", "copper_um": [70, 35, 35, 70]},
        "drill": {"plated": 131, "unplated": 42},
        "bom": {"full_rows": len(full_bom), "populated_rows": len(populated_bom)},
        "pnp": {"all_rows": len(all_pos), "populated_rows": len(populated_pos)},
        "dnp": sorted(DNP),
        "required_populated": sorted(REQUIRED_POPULATED),
        "files": [{"path": path.relative_to(output).as_posix(), "size": path.stat().st_size, "sha256": sha256(path)} for path in files],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    validate_inventory(output, EXPECTED_PACKAGE_PATHS, "final package")
    saved_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    saved_entries = saved_manifest.get("files", [])
    if [entry.get("path") for entry in saved_entries] != sorted(manifested_paths):
        raise SystemExit("unexpected manifest path inventory")
    for entry in saved_entries:
        path = output / entry["path"]
        if entry.get("size") != path.stat().st_size or entry.get("sha256") != sha256(path):
            raise SystemExit("manifest size or hash validation failed")
    print(json.dumps({"output": str(output), "commit": commit, "files": len(files) + 1, "gerber_layers": 11, "pth": 131, "npth": 42, "bom_populated_rows": len(populated_bom), "pnp_populated_rows": len(populated_pos), "fabrication_ready": False}, indent=2))


if __name__ == "__main__":
    main()
