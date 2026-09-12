# Production

Manufacturing outputs will be stored here only after the corresponding design revision passes pre-fabrication review.

Planned outputs:

- `gerber/` - Gerber and drill files
- `bom/` - BOM exports with manufacturer part numbers
- `assembly/` - pick-and-place, assembly drawings and build notes

Every manufacturing package must state the exact design revision and commit used to generate it.

Generate a release candidate only from a clean tracked worktree:

```bash
python production/generate_manufacturing_package.py
```

The default output is `production/releases/<commit-prefix>/`. The generator emits and validates Gerber, separate PTH/NPTH drill files, drill maps/report, full and populated BOMs, full and populated PnP files, top/bottom assembly PDFs, schematic PDF, a Gerber/drill ZIP and a SHA-256 manifest. KiCad generation timestamps and ZIP metadata are normalized to the source commit time, so repeated exports from the same commit and KiCad version are byte-for-byte identical. Every generated manifest remains `fabrication_ready=false` until physical and EVT gates are closed.

## PCB order specification

- Board count: one
- Outline: 65.00 × 30.90 mm Edge.Cuts centerline
- Layers: 4
- Finished thickness: 1.0 mm
- Material: FR-4
- Copper: 70 µm outer / 35 µm inner / 35 µm inner / 70 µm outer (approximately 2/1/1/2 oz)
- Surface finish: ENIG
- Solder mask: green
- Silkscreen: white, both sides
- Minimum drill files: separate PTH and NPTH Excellon, metric, absolute origin
- Assembly: both sides; DNP list must be excluded from populated BOM/PnP

The solder-mask and silkscreen colors are ordering choices; the electrical/geometry release is defined by the committed KiCad source and generated hashes.

## Mandatory assembly and operating notes

- Populate C45 as Murata `GRM32ER71H106KA12L` / LCSC `C77102` only after the assembled stack proves at least 4.0 mm PCB-surface gap and 0.5 mm residual clearance at the Radxa U1 overlap.
- Use controlled M2.5 spacers; connector friction must not define the board gap.
- Use 8 Ω speakers only and keep audio muted during host boot. The final audio limit comes from EVT current and undervoltage measurements.
- Do not power the Radxa USB-C input while the HAT battery input is energized.
- Use the Radxa external U.FL antenna unless OTA validation approves the onboard antenna under the full-size HAT.
- Additional 100–330 µF output capacitance is an EVT tack-on option across C21/C22, not a released production fit.
- `fabrication_ready=false` remains authoritative until all gates in `../docs/PROJECT_STATUS.md` are closed.
