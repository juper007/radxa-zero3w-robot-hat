# Power Footprint Verification Gate

Status: VERIFYING  
Date: 2026-09-09

## Purpose

Do not create a fabrication candidate from guessed package geometry. Critical power devices must use manufacturer package/land-pattern data and must be checked in KiCad before release.

## TPS259470ARPWR

Selected package: TI `RPW0010A`, 10-pin VQFN-HR / HotRod, nominal 2 mm x 2 mm, 0.45 mm pitch.

Verified electrical pin map:
1 EN/UVLO
2 OVLO
3 AUXOFF
4 FLT
5 IN
6 OUT
7 DVDT
8 GND
9 ILM
10 ITIMER

The TI Rev-C datasheet (May 2026) contains the `4225183/A` package outline and land-pattern example. This footprint is asymmetric and must not be replaced by a generic 2 x 2 mm QFN.

Project footprint:
`hardware/libraries/RadxaRobotHat.pretty/TI_RPW0010A_2x2mm_P0.45mm.kicad_mod`

The copper geometry now reproduces the TI land-pattern dimensions used by the design:
- pads 5/6: 0.30 x 2.40 mm central longitudinal lands
- middle side pads 2/3/8/9: 0.60 x 0.25 mm
- corner outer lands: 0.60 x 0.30 mm
- corner return lands: 0.25 x 0.65 mm
- duplicated pad numbers at HotRod corners are intentional

A CI checker locks the critical pad count/geometry against accidental replacement.

Current gate:
- [x] package family identified
- [x] electrical pin numbering identified
- [x] TI RPW0010A package drawing located
- [x] copper land pattern transcribed from TI example
- [x] automated pad-count/critical-geometry regression check added
- [ ] solder-paste apertures independently compared with TI stencil example
- [ ] footprint opened in KiCad 9 and visual pad-number review performed
- [ ] DRC performed in final PCB context

## BSC009NE2LS5I

Selected ordering code: `BSC009NE2LS5IATMA1`.

### Authoritative package identification

A prior draft first called this device `PG-TDSON-8-46`, then over-corrected it to `PG-TDSON-8-7`. Neither dash-variant claim is sufficiently supported by the BSC009NE2LS5I product-specific public data and **must not be used as the footprint authority**.

The authoritative BSC009NE2LS5I data establishes:
- package family: `PG-TDSON-8`
- package name: `SuperSO8`
- terminals: 8
- electrical mapping: pins 1/2/3 SOURCE, pin 4 GATE, pins 5/6/7/8 DRAIN
- nominal body class: approximately 5 x 6 mm SuperSO8
- terminal pitch: 1.27 mm

The product-specific datasheet includes the recommended PG-TDSON-8 boardpad and stencil-aperture drawing. That drawing, not a guessed dash variant, is the geometry authority for Q1.

### Manufacturer boardpad dimensions captured for implementation

From the Infineon PG-TDSON-8 recommended-boardpad drawing used by this product family:
- terminal pitch: 1.27 mm, 3 intervals
- small terminal copper size: 0.8 mm x 0.6 mm
- large drain copper width/length callouts: 3.325 mm and 2.863 mm
- overall copper span callout: 4.455 mm
- additional copper/solder-mask callouts: 0.5 mm and 0.925 mm
- stencil drawing callouts include 2.9 mm, 1.6 mm, 1.5 mm, 0.875 mm, 0.825 mm, 0.75 mm, 0.5 mm, 0.4 mm and 0.2 mm separations

These values are retained as the transcription checklist. The final KiCad pad geometry must be compared visually against the Infineon drawing before fabrication status can be granted.

### Current gate

- [x] exact ordering code frozen: `BSC009NE2LS5IATMA1`
- [x] package family confirmed as `PG-TDSON-8 / SuperSO8`
- [x] source/gate/drain pin numbering verified
- [x] manufacturer recommended boardpad/stencil drawing located
- [x] critical drawing dimensions captured in this gate document
- [ ] exact copper pad geometry transcribed into `RadxaRobotHat.pretty`
- [ ] pad-number mapping visually checked against source/gate/drain drawing
- [ ] exposed-drain paste aperture strategy reproduced or intentionally documented
- [ ] courtyard/clearance checked against main power pours
- [ ] footprint opened in KiCad and orientation visually reviewed
- [ ] board-level DRC performed

No generic SO-8 footprint and no dash-variant-specific footprint may be promoted as fabrication-ready unless the exact variant is independently proven for the selected ordering code.

## LM74700QDBVRQ1

Package: TI DBV SOT-23-6.

Electrical pin numbering is already verified. Standard KiCad SOT-23-6 is acceptable only after the TI top-view numbering is checked against the selected library footprint in the integrated schematic.

## Project library registration

`hardware/kicad/fp-lib-table` registers `${KIPRJMOD}/../libraries/RadxaRobotHat.pretty` as `RadxaRobotHat`.

## Automated verification

`hardware/kicad/check_footprints.py` currently checks the critical TI RPW footprint invariants. `.github/workflows/footprint-check.yml` runs it on footprint changes.

The checker must be expanded to validate BSC009 PG-TDSON-8 geometry after the footprint is added.

This CI check is a regression guard, not a substitute for KiCad DRC or physical/visual footprint review.

## Connector/fuse footprints

XT60 and the 20 A fuse remain mechanical choices. A board-mount XT60 is allowed only if it fits without violating the Radxa outline/connector clearances; heavy pigtail through-holes remain the fallback.

## Fabrication gate

Power footprints remain **NOT YET FABRICATION-APPROVED**. TPS25947 transcription is substantially complete. Q1 is now correctly constrained to the BSC009NE2LS5I product-specific PG-TDSON-8/SuperSO8 drawing; its exact copper/stencil footprint still must be transcribed, visually checked and board-level DRC reviewed.
