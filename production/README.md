# Production

Manufacturing outputs will be stored here only after the corresponding design revision passes pre-fabrication review.

Planned outputs:

- `gerber/` - Gerber and drill files
- `bom/` - BOM exports with manufacturer part numbers
- `assembly/` - pick-and-place, assembly drawings and build notes

Every manufacturing package must state the exact design revision and commit used to generate it.

Purchasing identity is resolved from both `Man.` / `Man. Ref.` and
`Manufacturer_Name` / `Manufacturer_Part_Number`. Conflicting non-empty fields
fail export rather than silently choosing one. Both full and populated BOMs
must identify J4 as **Toby Electronics / REF-182665-01**, without an unrelated
LCSC substitute. J4 is also mandatory in populated BOM and PnP inventories.

Run the native BOM regression without generating an order package:

```bash
RUN_BOM_INTEGRATION=1 python production/test_generate_manufacturing_package.py
```

Historical packages, including `releases/7f1aef08/`, predate this purchasing-field
correction and contain blank J4 manufacturer/MPN columns. Do not use them for
assembly ordering. Regenerate only after review and an approved clean commit;
do not edit old packages or their manifests in place.

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

- Stage 2 requires Q3/Q4/Q5, R42–R46 and the revised R24/R3 values; D2 is replaced, not an optional DNP shortcut. Every connector is mandatory in both BOM and the position inventory.
- Position CSVs now include SMT and THT connectors, test points and fiducials. The assembler must select actual fitted parts and SMT/THT operations using the BOM and footprint drawings; do not load this complete inventory directly into an SMT placement machine.
- Current full/populated BOM rows: 130/121. Full/populated position rows: 133/124. Drill totals: 150 PTH and 42 NPTH. Older SMD-only counts and release packages are historical, not current assembly inputs.

- Populate J5/J6/J7/J8 and R18/R19/R20/R21/R34/R35/R38/R39. Omitting the auxiliary connectors or their 0 Ω/pull-up networks breaks upstream functional parity.
- Install and validate `../software/overlays/radxa-zero3w-robot-hat-qwiic.dts` on the intended Radxa OS image before accepting J6/J7/J8 operation.
- Populate C45 as Murata `GRM32ER71H106KA12L` / LCSC `C77102` only after the assembled stack proves at least 4.0 mm PCB-surface gap and 0.5 mm residual clearance at the Radxa U1 overlap.
- For the representative EVT stack, control the PCB-surface gap at 9.5 mm and
  use M2 fasteners; connector friction must not define the gap. This is not a
  production-approved spacer MPN or tolerance stack.
- Use 8 Ω speakers only and keep audio muted during host boot. The final audio limit comes from EVT current and undervoltage measurements.
- Do not power the Radxa USB-C input while the HAT battery input is energized.
- Use the Radxa external U.FL antenna unless OTA validation approves the onboard antenna under the full-size HAT.
- Additional 100–330 µF output capacitance is an EVT tack-on option across C21/C22, not a released production fit.
- `fabrication_ready=false` remains authoritative until all gates in `../docs/PROJECT_STATUS.md` are closed.
