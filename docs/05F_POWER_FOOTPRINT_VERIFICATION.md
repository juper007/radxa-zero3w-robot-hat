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

Project footprint:
`hardware/libraries/RadxaRobotHat.pretty/TI_RPW0010A_2x2mm_P0.45mm.kicad_mod`

The copper geometry reproduces the TI land-pattern dimensions used by the design and is guarded by CI.

Current gate:
- [x] package family identified
- [x] electrical pin numbering identified
- [x] TI RPW0010A package drawing located
- [x] copper land pattern transcribed
- [x] automated geometry regression check added
- [ ] solder-paste apertures independently compared with TI stencil example
- [ ] footprint opened in KiCad 9 and visually reviewed
- [ ] DRC performed in final PCB context

## BSC009NE2LS5I

Selected ordering code: `BSC009NE2LS5IATMA1`.

Infineon identifies this device as:
- package family: `PG-TDSON-8`
- package name: `SuperSO8`
- 8 terminals
- 1.27 mm pitch
- source pins 1/2/3
- gate pin 4
- drain pins 5/6/7/8

Unsupported earlier assertions about a dash-number package variant have been removed. The authoritative geometry source is the Infineon PG-TDSON-8 recommended boardpad/stencil drawing for this SuperSO8 family.

Project footprint:
`hardware/libraries/RadxaRobotHat.pretty/Infineon_PG-TDSON-8_SuperSO8.kicad_mod`

The implemented footprint uses the manufacturer boardpad geometry and was cross-checked against KiCad's established `TDSON-8-1` reference footprint. Important geometry includes:
- terminal pitch: 1.27 mm
- four source/gate pads on the left side
- large drain copper region
- four drain lead-edge copper contacts mapped to electrical pins 5–8
- segmented paste apertures over the large drain region
- separate paste apertures at drain lead exits

Electrical mapping is intentionally explicit even though the physical drain leadframe is one continuous conductor. This keeps the existing schematic symbol pins 5/6/7/8 valid while preserving the manufacturer copper shape.

Current gate:
- [x] package family identified as PG-TDSON-8 / SuperSO8
- [x] source/gate/drain pin numbering identified
- [x] manufacturer boardpad/stencil dimensions located
- [x] footprint transcribed into project library
- [x] CI geometry checks added for pins 1–8, pitch, large drain copper and paste apertures
- [x] GitHub `Footprint geometry sanity check` run #3 passed after BSC009 checks were added
- [ ] footprint opened in KiCad 9 and pad numbering visually reviewed
- [ ] overlapping drain electrical pads reviewed in KiCad DRC context
- [ ] stencil/paste coverage independently reviewed before production
- [ ] courtyard/clearance checked in final high-current placement

## LM74700QDBVRQ1

Package: TI DBV SOT-23-6.

Electrical pin numbering is verified. Standard KiCad SOT-23-6 remains acceptable only after top-view pin-1 orientation is checked in the integrated schematic/PCB.

## Project library registration

`hardware/kicad/fp-lib-table` registers `${KIPRJMOD}/../libraries/RadxaRobotHat.pretty` as `RadxaRobotHat`.

## Automated verification

`hardware/kicad/check_footprints.py` now checks both:
- TPS259470A RPW HotRod geometry
- BSC009 PG-TDSON-8 / SuperSO8 geometry

`.github/workflows/footprint-check.yml` runs this checker on footprint changes.

The CI checker is a regression guard, not a substitute for KiCad DRC or a visual manufacturer-drawing review.

## Connector/fuse footprints

XT60 and the 20 A fuse remain mechanical choices. A board-mount XT60 is allowed only if it fits the final Radxa outline without violating keepouts; heavy pigtail through-holes remain the fallback.

## Fabrication gate

Power footprints are materially closer to release, but remain **NOT FABRICATION-APPROVED** until KiCad visual review, stencil review and board-level DRC are complete.
