# Immediate mechanical handoff

Verified exact J4 KiCad model block: see `J4_PLACEMENT.md` (native exported peg centers confirmed).

Critical exercised CAD result at **4.0 mm exported mask-to-host-top gap**:
- C45 generic nominal model vs official Radxa: **0.665 mm**, no solid overlap.
- Exact J4 vs official Radxa: **498.317309947 mm³ solid overlap**; **478.029759678 mm³** lies below host header plastic top in the header-body diagnostic region. This is major connector body interference, NOT ordinary intended contact.
- At 6.2 mm gap the below-header-top interference becomes zero, but the complete solids still overlap 48.50638 mm³ at the contact/pin region. This is NOT a qualified alternate stack or approved spacer recommendation.
- Supplier C45 datasheet gives **2.5 ±0.2 mm thickness**. Generic model is 2.5 mm, NOT max material. Nominal 4mm spacing alone does not guarantee the required residual 0.5mm across tolerance.
- Existing document XY transform is approximate, NOT exact current-STEP hole alignment. Header grid-derived native KiCad STEP -> Radxa transform:
  **translate `(-70.947472, 106.31508, 4.085)` mm**, no rotation, when the KiCad STEP is exported with `--user-origin 0x0mm`.
  PCB XY convention: `Xr=Xhat-70.947472`, `Yr=106.31508-Yhat`.
  4.085 Z incorporates exported HAT bottom mask bound -0.085; host top reference is Z=0.
- For rendering host into unshifted native HAT STEP instead, use inverse translation **`(+70.947472,-106.31508,-4.085)` mm**. Do not mix this with a KiCad footprint model-local offset; that requires independent conversion.
- Host STEP contains a header with tip Z=8.5 and plastic top Z=2.5; it is NOT the same thing as an approved physical male-header MPN.

Full final-source checks are complete: see `CAD_REPORT.md`, `cad_evidence.json`, `j4_evidence.json`, and the two `stack_4mm*.png` actual CAD renders. Final PCB SHA256 is `10decd01363cee7c002294a6e6b6dbfa8d8b9488eec4e8337256af82ff02f592`. Final exact licensed J4 and stack STEP exports stay in `C:/Users/juper/AppData/Local/Temp/radxa-cad-final`, not public Git. **Additional critical result: C7-to-host USB-C CAD separation is only 0.005 mm at the same 4 mm gap; C6/C8/C9/FB2/FB3 are 0.305 mm.** Header-aligned mounting-axis residuals reach 0.269105 mm, so simultaneous screw/header fit is not established.
