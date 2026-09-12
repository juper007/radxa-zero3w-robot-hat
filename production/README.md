# Production

Manufacturing outputs will be stored here only after the corresponding design revision passes pre-fabrication review.

Planned outputs:

- `gerber/` - Gerber and drill files
- `bom/` - BOM exports with manufacturer part numbers
- `assembly/` - pick-and-place, assembly drawings and build notes

Every manufacturing package must state the exact design revision and commit used to generate it.

## Mandatory assembly and operating notes

- Populate C45 as Murata `GRM32ER71H106KA12L` / LCSC `C77102` only after the assembled stack proves at least 4.0 mm PCB-surface gap and 0.5 mm residual clearance at the Radxa U1 overlap.
- Use controlled M2.5 spacers; connector friction must not define the board gap.
- Use 8 Ω speakers only and keep audio muted during host boot. The final audio limit comes from EVT current and undervoltage measurements.
- Do not power the Radxa USB-C input while the HAT battery input is energized.
- Use the Radxa external U.FL antenna unless OTA validation approves the onboard antenna under the full-size HAT.
- Additional 100–330 µF output capacitance is an EVT tack-on option across C21/C22, not a released production fit.
- `fabrication_ready=false` remains authoritative until all gates in `../docs/PROJECT_STATUS.md` are closed.
