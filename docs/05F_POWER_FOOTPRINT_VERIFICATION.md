# Power Footprint Verification Gate

Status: VERIFYING  
Date: 2026-09-10

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

Validation review on 2026-09-10 rechecked the product-specific Infineon package information. The selected ordering code maps to the `PG-TDSON-8-7` variant in the SuperSO8 / PG-TDSON-8 family. Earlier repo text that removed the dash-variant designation was overly conservative and is corrected here.

Verified electrical mapping:
- source pins 1/2/3
- gate pin 4
- drain pins 5/6/7/8
- terminal pitch 1.27 mm

Project footprint:
`hardware/libraries/RadxaRobotHat.pretty/Infineon_PG-TDSON-8_SuperSO8.kicad_mod`

The current footprint geometry remains valid after the package-variant correction: the implemented land pattern uses the product-specific SuperSO8 boardpad dimensions, including the four source/gate lands, large drain copper region, four drain edge contacts and segmented paste apertures. The file name remains family-based to avoid unnecessary library churn; the documentation is explicit that the selected BSC009 ordering code is the PG-TDSON-8-7 variant.

Current gate:
- [x] package identified as PG-TDSON-8-7 within SuperSO8 family
- [x] source/gate/drain pin numbering identified
- [x] manufacturer boardpad/stencil dimensions located
- [x] footprint transcribed into project library
- [x] CI geometry checks added for pins 1-8, pitch, large drain copper and paste apertures
- [ ] footprint opened in KiCad 9 and pad numbering visually reviewed
- [ ] overlapping drain electrical pads reviewed in KiCad DRC context
- [ ] stencil/paste coverage independently reviewed before production
- [ ] courtyard/clearance checked in final high-current placement

## High-current servo branch net tie

Validation found that the earlier `0R_LINK` / 2512 representation for the three servo power branches was not justified for the branch current envelope. A five-XL330 branch has a theoretical stall current of about 7.35 A, so a generic zero-ohm resistor is no longer allowed in this path.

Replacement footprint:
`hardware/libraries/RadxaRobotHat.pretty/HighCurrent_NetTie_2Pin_8mm.kicad_mod`

Design intent:
- NTA/NTB/NTC are copper net ties, not resistors
- approximately 8 mm transverse copper width
- short connection between `+5V_SYS` and each branch rail
- no solder paste and no BOM/PnP component
- final implementation uses 2 oz outer copper and must be checked in board-level DRC/thermal review

`check_footprints.py` rejects loss of the net-tie declaration, 8 mm pad geometry or accidental solder-paste apertures.

## LM74700QDBVRQ1

Package: TI DBV SOT-23-6.

Electrical pin numbering is verified. Standard KiCad SOT-23-6 remains acceptable only after top-view pin-1 orientation is checked in the integrated schematic/PCB.

## Automated verification

`hardware/kicad/check_footprints.py` checks:
- TPS259470A RPW HotRod geometry
- BSC009 PG-TDSON-8-7 / SuperSO8 geometry
- high-current 8 mm servo-branch net-tie geometry

The CI checker is a regression guard, not a substitute for KiCad DRC or visual manufacturer-drawing review.

## Connector/fuse footprints

XT60 and the 20 A fuse remain mechanical choices. A board-mount XT60 is allowed only if it fits the final Radxa outline without violating keepouts; heavy pigtail through-holes remain the fallback.

## Fabrication gate

Power footprints are materially closer to release, but remain **NOT FABRICATION-APPROVED** until KiCad visual review, stencil review and board-level DRC are complete.
