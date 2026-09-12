#!/usr/bin/env python3
"""Regression tests for manufacturing-package output safety."""

from __future__ import annotations

import hashlib
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import generate_manufacturing_package as generator


class OutputPathTests(unittest.TestCase):
    def test_accepts_child_of_release_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            releases = Path(directory) / "production" / "releases"
            expected = (releases / "candidate").resolve()

            self.assertEqual(
                generator.validated_output_path(expected, releases),
                expected,
            )

    def test_rejects_release_directory_itself(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            releases = Path(directory) / "production" / "releases"

            with self.assertRaisesRegex(SystemExit, "must be a child directory"):
                generator.validated_output_path(releases, releases)

    def test_rejects_path_outside_release_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            production = Path(directory) / "production"
            releases = production / "releases"

            with self.assertRaisesRegex(SystemExit, "must be inside"):
                generator.validated_output_path(production, releases)


class ReproducibilityTests(unittest.TestCase):
    def test_normalizes_kicad_generation_timestamps(self) -> None:
        self.assertEqual(
            generator.normalized_kicad_bytes(
                b"%TF.CreationDate,2026-09-12T06:07:39-07:00*%\r\n"
                b"G04 Created by KiCad (PCBNEW 10.0.6) date 2026-09-12 06:07:39*\r\n",
                946684800,
                f"{generator.BOARD_NAME}-F_Cu.gtl",
            ),
            b"%TF.CreationDate,2000-01-01T00:00:00+00:00*%\r\n"
            b"G04 Created by KiCad (PCBNEW 10.0.6) date 2000-01-01 00:00:00*\r\n",
        )
        self.assertEqual(
            generator.normalized_kicad_bytes(
                b"/CreationDate (D:2026:09:12:06:07:39)\n"
                b"VISIBLE /CreationDate (D:2026:09:12:06:07:39) DESIGN NOTE\n",
                946684800,
                "assembly_top.pdf",
            ),
            b"/CreationDate (D:2000:01:01:00:00:00)\n"
            b"VISIBLE /CreationDate (D:2026:09:12:06:07:39) DESIGN NOTE\n",
        )
        self.assertEqual(
            generator.normalized_kicad_bytes(
                b"Created on 2026-09-12T06:07:39\n"
                b"Created on 2026-09-12T06:07:39 VISIBLE DESIGN NOTE\n",
                946684800,
                "drill_report.txt",
            ),
            (
                b"Created on 2000-01-01T00:00:00\n"
                b"Created on 2026-09-12T06:07:39 VISIBLE DESIGN NOTE\n"
            ),
        )

    def test_does_not_normalize_unknown_file_types(self) -> None:
        source = b"%TF.CreationDate,2026-09-12T06:07:39-07:00*%\n"
        self.assertEqual(generator.normalized_kicad_bytes(source, 946684800, "notes.txt"), source)

    def test_does_not_normalize_unknown_generated_filename(self) -> None:
        source = b"%TF.CreationDate,2026-09-12T06:07:39-07:00*%\n"
        self.assertEqual(generator.normalized_kicad_bytes(source, 946684800, "unknown.gtl"), source)

    def test_rejects_wrong_kicad_version_metadata(self) -> None:
        source = (
            b"%TF.CreationDate,2026-09-12T06:07:39-07:00*%\n"
            b"G04 Created by KiCad (PCBNEW 99.9.9) date 2026-09-12 06:07:39*\n"
        )
        with self.assertRaisesRegex(SystemExit, "Gerber comment date"):
            generator.normalized_kicad_bytes(
                source,
                946684800,
                f"{generator.BOARD_NAME}-F_Cu.gtl",
            )

    def test_rejects_wrong_kicad_drill_version_metadata(self) -> None:
        source = (
            b"; DRILL file KiCad 99.9.9 date 2026-09-12T06:07:39\n"
            b"; #@! TF.CreationDate,2026-09-12T06:07:39-07:00\n"
        )
        with self.assertRaisesRegex(SystemExit, "drill comment date"):
            generator.normalized_kicad_bytes(
                source,
                946684800,
                f"{generator.BOARD_NAME}-PTH.drl",
            )

    def test_writes_zip_independent_of_source_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.txt"
            source.write_text("stable content\n", encoding="utf-8")
            first = root / "first.zip"
            second = root / "second.zip"

            os.utime(source, (1000000000, 1000000000))
            generator.write_deterministic_zip(first, root, [source], 946684800)
            os.utime(source, (1100000000, 1100000000))
            generator.write_deterministic_zip(second, root, [source], 946684800)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(archive.infolist()[0].date_time, (2000, 1, 1, 0, 0, 0))

    def test_zip_timestamp_uses_two_second_resolution(self) -> None:
        self.assertEqual(generator.zip_date_time(946684801), (2000, 1, 1, 0, 0, 0))

    @unittest.skipUnless(os.environ.get("RUN_KICAD_INTEGRATION") == "1", "requires KiCad integration")
    def test_full_export_is_byte_reproducible(self) -> None:
        releases = generator.RELEASES
        first = releases / "ci-repro-first"
        second = releases / "ci-repro-second"
        self.addCleanup(shutil.rmtree, first, True)
        self.addCleanup(shutil.rmtree, second, True)

        for output in (first, second):
            result = subprocess.run(
                [sys.executable, str(Path(generator.__file__)), "--output", str(output), "--force"],
                cwd=generator.REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode:
                self.fail(f"manufacturing export failed\n{result.stdout}\n{result.stderr}")

        def hashes(root: Path) -> dict[str, str]:
            return {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(root.rglob("*"))
                if path.is_file()
            }

        first_hashes = hashes(first)
        self.assertEqual(len(first_hashes), 27)
        self.assertEqual(first_hashes, hashes(second))


class ExportPolicyTests(unittest.TestCase):
    def test_declares_complete_board_dnp_inventory(self) -> None:
        self.assertEqual(
            generator.DNP,
            {
                "C25", "R10", "R11", "R16", "R17", "R36", "R37", "R41", "U4",
            },
        )

    def test_requires_all_four_qwiic_ports_in_populated_exports(self) -> None:
        self.assertTrue(
            {
                "J5", "J6", "J7", "J8", "R18", "R19", "R20", "R21",
                "R34", "R35", "R38", "R39",
            }
            <= generator.REQUIRED_POPULATED
        )

    def test_requires_audio_connectors_in_populated_exports(self) -> None:
        self.assertTrue({"J1", "J2", "J9"} <= generator.REQUIRED_POPULATED)

    def test_rejects_required_reference_missing_from_populated_bom(self) -> None:
        with self.assertRaisesRegex(SystemExit, "required populated references missing from BOM"):
            generator.validate_required_populated(set(), {"J1"}, required={"J1"})

    def test_rejects_required_reference_missing_from_populated_pnp(self) -> None:
        with self.assertRaisesRegex(SystemExit, "required populated references missing from PnP"):
            generator.validate_required_populated({"J1"}, set(), required={"J1"})

    def test_rejects_unexpected_export_omission(self) -> None:
        with self.assertRaisesRegex(SystemExit, "BOM reference inventory"):
            generator.validate_reference_exports(
                full_bom_refs={"A", "B", "EXTRA"},
                populated_bom_refs={"A"},
                all_pos_refs={"A", "B"},
                populated_pos_refs={"A"},
                dnp={"B"},
            )

    def test_expected_package_inventory_is_exact(self) -> None:
        self.assertEqual(len(generator.EXPECTED_EXPORT_PATHS), 24)
        self.assertEqual(len(generator.EXPECTED_ARCHIVE_PATHS), 17)
        self.assertEqual(len(generator.EXPECTED_PACKAGE_PATHS), 27)


if __name__ == "__main__":
    unittest.main()
