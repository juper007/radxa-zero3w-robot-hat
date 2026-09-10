# Power Footprint Verification Gate

Status: VERIFYING  
Date: 2026-09-09

## Purpose

Do not create a fabrication candidate from guessed package geometry. The power devices carry either high current or directly protect the Radxa host, so package pin numbering and manufacturer land patterns must be verified before PCB placement is frozen.

## TPS259470ARPWR

Selected package family: TI RPW, 10-pin VQFN-HR, nominal 2 mm x 2 mm.

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

TI publishes package drawing `RPW0010A`. The manufacturer land-pattern drawing, not a visually similar generic 2x2 QFN, is authoritative.

Current gate:
- [x] package family identified
- [x] electrical pin numbering identified
- [x] TI RPW0010A package drawing located
- [ ] every copper pad dimension transcribed and independently checked
- [ ] solder-mask expansion strategy checked
- [ ] paste apertures checked
- [ ] footprint opened in KiCad and pad numbers visually reviewed

Until all remaining boxes are complete, a custom TPS25947 footprint must be marked UNVERIFIED and excluded from fabrication release.

## BSC009NE2LS5I

Selected package: Infineon SuperSO8 / PG-TDSON-8 family, approximately 5x6 mm power package.

Verified electrical mapping:
- pins 1,2,3 = SOURCE
- pin 4 = GATE
- pins 5,6,7,8 = DRAIN

The package uses a large drain-side thermal/current pad geometry. The Infineon recommended PCB pad design is authoritative; a generic SO-8 footprint is not automatically acceptable even if the leads appear compatible.

Current gate:
- [x] package family identified
- [x] source/gate/drain pin numbering identified
- [x] Infineon recommended-board-assembly drawing located
- [ ] exact recommended copper geometry transcribed
- [ ] drain copper/paste strategy checked for assembly
- [ ] courtyard/clearance checked against nearby high-current copper
- [ ] footprint opened in KiCad and source/drain orientation visually reviewed

## LM74700QDBVRQ1

Package: TI DBV SOT-23-6.

This package can use the standard KiCad SOT-23-6 land pattern only after pad numbering is compared with the TI DBV package view. Electrical mapping is already verified and CI protects the SOURCE/ANODE and DRAIN/CATHODE topology.

## Connector/fuse footprints

XT60 and the 20 A fuse remain mechanical choices, not merely schematic choices. Board-mount XT60 is allowed only if it fits the ~65x30 mm board without violating Radxa connector/enclosure clearance. A short heavy pigtail soldered to large plated through-holes is the fallback and may be mechanically preferable.

## Fabrication gate

Power footprint status is currently **NOT VERIFIED FOR FABRICATION**. Schematic development may continue in parallel, but PCB manufacturing outputs cannot move to FAB-CANDIDATE until the package drawings are transcribed, reviewed and DRC-tested.
