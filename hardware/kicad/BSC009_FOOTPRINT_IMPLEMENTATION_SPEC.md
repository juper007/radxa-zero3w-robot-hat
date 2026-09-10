# BSC009NE2LS5I Footprint Implementation Spec

Status: DESIGNING / manufacturer-derived, not fabrication-approved  
Target device: `BSC009NE2LS5IATMA1`

## Authority

Use the BSC009NE2LS5I product-specific Infineon datasheet and its PG-TDSON-8 / SuperSO8 recommended boardpad and stencil-aperture drawing.

Do **not** use a guessed `PG-TDSON-8-x` dash variant as the footprint authority unless Infineon explicitly maps the selected ordering code to that exact variant.

## Electrical pad mapping

- pins 1, 2, 3 = SOURCE
- pin 4 = GATE
- pins 5, 6, 7, 8 = DRAIN

The footprint must preserve all eight logical pad numbers even though the drain side is intentionally a large, low-resistance copper structure.

## Manufacturer dimensions captured

Package outline / electrical:
- package family: PG-TDSON-8 / SuperSO8
- nominal body class: approximately 5 mm x 6 mm
- pitch: 1.27 mm
- 8 terminals
- exposed/extended drain copper region

Recommended boardpad drawing callouts:
- four small terminal locations on 1.27 mm pitch
- small terminal copper: 0.8 mm x 0.6 mm
- large drain-copper callouts: 3.325 mm and 2.863 mm
- overall copper span callout: 4.455 mm
- other copper/mask callouts: 0.5 mm and 0.925 mm

Stencil drawing callouts captured for independent reconstruction/review:
- 2.9 mm
- 1.6 mm
- 1.5 mm
- 0.875 mm
- 0.825 mm
- 0.75 mm
- 0.5 mm
- 0.4 mm
- 0.2 mm separation features

## KiCad implementation rules

1. Use a dedicated project-local footprint under `hardware/libraries/RadxaRobotHat.pretty/`.
2. Preserve pad numbers 1 through 8 exactly.
3. Source pads 1/2/3 must join the source-side high-current copper without routing through the gate pad region.
4. Gate pad 4 must remain isolated from source/drain high-current copper and have a short, quiet route to LM74700 GATE.
5. Drain pads 5/6/7/8 must form a very low-resistance connection to `+5V_SYS` and may merge into a common copper region only if KiCad net/pad numbering remains valid and DRC-clean.
6. Solder-paste apertures for the large drain region must be split according to the manufacturer stencil intent rather than using one solid paste opening.
7. Courtyard must represent the actual package body plus assembly clearance, not merely the copper land extents.
8. Pin-1 orientation mark must agree with both the Infineon package view and the project symbol mapping.
9. No thermal-relief spokes on the main source/drain current corridor unless current/assembly review explicitly justifies them.
10. Provide substantial top/bottom copper and via stitching around the drain/source current corridor in PCB layout; footprint copper alone is not the thermal design.

## Validation gate

Before this footprint can become `FAB_APPROVED`:
- [ ] copper geometry recreated from Infineon drawing
- [ ] paste apertures recreated/reviewed
- [ ] all pad centers/sizes measured against manufacturer callouts
- [ ] pin-1 orientation visually checked
- [ ] pad numbers 1..8 checked against symbol
- [ ] footprint opened in KiCad 9
- [ ] footprint checker extended with geometry invariants
- [ ] final board DRC clean
- [ ] Q1 high-current copper reviewed in PCB context

Until all boxes are complete, use status `DRAFT_FOOTPRINT` only.
