# Project Status

Last updated: 2026-09-10

## Current phase

**Validation correction pass + Phase 1 power + Phase 2 Dynamixel TTL + Phase 3 sensors + Phase 4 audio/top-level integration**

## Validation corrections completed

- [x] Rechecked KiCad 74LVC1G08/125/126 symbol definitions against upstream Pollen source
- [x] Corrected the validation misconception about U5/U6/U7 VCC/GND orientation: in this legacy orientation VCC is the +400 mil Y anchor and GND is the -400 mil Y anchor
- [x] Corrected `dynamixel_v17_import.sch` to the verified U5/U6/U7 VCC/GND/OE anchors
- [x] Restored upstream R31 = 10k pull-up from +3V3 to `TTL_RX_OUT`
- [x] Restored upstream R32 = 10k pull-up from +3V3 to `DXL_LOCAL`
- [x] Added R31/R32 to connectivity contract, BOM and both Dynamixel CI checkers
- [x] Removed generic 0-ohm / 2512 parts as the servo-branch high-current links from the authoritative power contract
- [x] Replaced them with NTA/NTB/NTC 8 mm copper net ties
- [x] Added project footprint `HighCurrent_NetTie_2Pin_8mm.kicad_mod`
- [x] Regenerated populated power import draft as `power_v17_import.sch` using NTA/NTB/NTC
- [x] Updated power schematic checker and workflow to use `power_v17_import.sch` and reject the superseded resistor-link implementation
- [x] Extended power and footprint CI to reject stale zero-ohm links and require the copper net-tie geometry
- [x] Rechecked BSC009NE2LS5IATMA1 package identity and documented the product-specific `PG-TDSON-8-7` variant within the SuperSO8 family

## Completed architecture

- [x] V1 frozen to external regulated 5 V high-current input; no onboard high-power buck
- [x] Servo and Radxa current paths separated
- [x] 4-layer / 2 oz outer-copper high-current strategy defined
- [x] LM74700QDBVRQ1 + BSC009NE2LS5I ideal-diode path selected
- [x] TPS259470ARPWR Radxa host branch selected
- [x] TPS25947 first-pass ILIM/dVdt/OVLO values frozen
- [x] TPS25947 RPW and BSC009 SuperSO8 footprints created and covered by geometry checks
- [x] DYNAMIXEL U7 TX / U6 RX / U5 combiner topology recovered
- [x] Automatic direction generator Q1/R26/R27/R28 recovered
- [x] R31/R32 required pull-ups restored from upstream
- [x] R33 = 150 ohm between `DXL_LOCAL` and `DXL_DATA` recovered
- [x] TTL-only RS-485 DNP input bias policy defined
- [x] Current MicroDuck `/dev/ttyS2`, 1 Mbps and `imu_to_dxl` architecture incorporated
- [x] BMI088 reclassified optional/DNP
- [x] Sensor/I2C, audio and top-level contracts/checkers exist

## Key electrical targets

- XL330 supply: regulated 5 V
- XL330 stall current: ~1.47 A each at 5 V
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- servo branch split: NTA/NTB/NTC copper net ties, approximately 8 mm width; no 0-ohm resistor element
- development supply: regulated 5 V, 15–20 A class
- TPS259470A host current-limit target: ~4.05 A calculated typical
- host startup ramp target: ~9.75 ms
- host OVLO target: ~5.69 V nominal
- BSC009 selected package: PG-TDSON-8-7 / SuperSO8 family
- DYNAMIXEL: `/dev/ttyS2`, 1 Mbps, Protocol V2
- DYNAMIXEL population: 15 XL330 + imu_to_dxl
- DXL local pull-up: R32 = 10k to +3V3
- TTL receive-output pull-up: R31 = 10k to +3V3
- DXL external series resistor: R33 = 150 ohm

## Current implementation state

### Power
`power_v17_import.sch` is now the current validation-corrected populated import draft. It contains the LM74700/BSC009 protected 5 V path, TPS259470A Radxa branch, support passives, host capacitors, and three servo rails split through NTA/NTB/NTC high-current copper net ties. `power_v1_connectivity.csv`, BOM, import checker, power CI and footprint CI are aligned to this implementation. `power_v16_import.sch` is superseded and must not be used for fabrication. Real KiCad 9 ERC/DRC is still pending.

### DYNAMIXEL
`dynamixel_v17_import.sch` is the current validation-corrected import draft. U5/U6/U7 VCC/GND/OE anchors were rechecked against upstream KiCad symbol definitions, and R31/R32 pull-ups are restored. `dynamixel_v15_import.sch` is superseded. Real KiCad 9 ERC is still pending.

### Footprints
TPS25947 RPW, BSC009 PG-TDSON-8-7/SuperSO8 and the 8 mm high-current branch net tie have project footprints and structural geometry checks. Real KiCad visual/DRC/stencil review is still required.

### Sensors / Audio / Top level
Architecture contracts and CI exist, but populated native KiCad implementations remain incomplete. Audio passive/reference network recovery is still pending.

## Immediate execution order

1. Confirm the new `power_v17_import.sch` connectivity/structure CI is green.
2. In a KiCad 9-capable environment, import/save corrected Dynamixel and power sheets and run real ERC.
3. Recover exact upstream audio codec/amplifier/MEMS passive network.
4. Populate sensors/audio schematics and top-level hierarchy.
5. Freeze XL330/imu_to_dxl connector orientation and mechanical footprint.
6. Freeze board outline/header/mounting holes/connector keepouts.
7. Place high-current corridor and route 4-layer PCB.
8. Run final ERC/DRC, power integrity and 1 Mbps bus bench validation.
9. Generate Gerber/BOM/PnP only after independent pre-fabrication review.

## Fabrication blockers

- real KiCad 9 ERC/DRC has not been run
- high-current copper net ties need final PCB-context DRC/thermal/current-path review
- BSC009/TPS25947 visual pad/stencil review incomplete
- XL330/imu_to_dxl connector orientation/polarity not mechanically frozen
- audio populated schematic incomplete
- sensors/top-level native hierarchy incomplete
- PCB placement/routing incomplete
- no Gerber is approved

## Current release status

`v0.17-dev` — validation-corrected populated drafts now exist for both Dynamixel and power. R31/R32 are restored, U5/U6/U7 anchors are rechecked, generic 0-ohm servo links are removed, and power v17 uses explicit 8 mm copper net ties. **Not fabrication-ready.**
