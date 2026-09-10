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

Manufacturer package has now been narrowed further to **Infineon PG-TDSON-8-46 / SuperSO8 5x6**. Infineon reports exposed paddle, body approximately 5.9 x 5.15 mm, 8 terminals and 1.27 mm terminal pitch. The BSC009NE2LS5I material/package record identifies PG-TDSON-8-46.

Verified electrical mapping:
- pins 1,2,3 = SOURCE
- pin 4 = GATE
- pins 5,6,7,8 = DRAIN

Current gate:
- [x] package family identified
- [x] exact `PG-TDSON-8-46` variant identified
- [x] source/gate/drain pin numbering identified
- [x] package outline dimensions verified
- [ ] exact Infineon footprint-drawing copper geometry transcribed
- [ ] exposed-drain copper/paste strategy checked
- [ ] courtyard/clearance checked against main power pours
- [ ] footprint opened in KiCad and orientation visually reviewed

No provisional generic SO-8 footprint will be promoted as fabrication-ready.

## LM74700QDBVRQ1

Package: TI DBV SOT-23-6.

Electrical pin numbering is already verified. Standard KiCad SOT-23-6 is acceptable only after the TI top-view numbering is checked against the selected library footprint in the integrated schematic.

## Project library registration

`hardware/kicad/fp-lib-table` now registers `${KIPRJMOD}/../libraries/RadxaRobotHat.pretty` as `RadxaRobotHat`.

## Automated verification

`hardware/kicad/check_footprints.py` checks the critical TI RPW footprint invariants. `.github/workflows/footprint-check.yml` runs it on footprint changes.

This CI check is a regression guard, not a substitute for KiCad DRC or physical/visual footprint review.

## Connector/fuse footprints

XT60 and the 20 A fuse remain mechanical choices. A board-mount XT60 is allowed only if it fits without violating the Radxa outline/connector clearances; heavy pigtail through-holes remain the fallback.

## Fabrication gate

Power footprints remain **NOT YET FABRICATION-APPROVED**. TPS25947 transcription is substantially complete, but the BSC009 recommended land pattern, visual KiCad review, solder-paste review and board-level DRC remain blockers.
