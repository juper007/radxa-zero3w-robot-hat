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
`power_v1_connectivity.csv` and the BOM now use NTA/NTB/NTC high-current copper net ties instead of generic 0-ohm / 2512 links. The project-local 8 mm net-tie footprint exists and is covered by geometry CI. The older `power_v16_import.sch` still contains the superseded resistor-link representation and is **NOT AUTHORITATIVE / DO NOT USE FOR FABRICATION**. It must be regenerated or converted to a v0.17 import/native sheet using NTA/NTB/NTC before KiCad ERC.

### DYNAMIXEL
`dynamixel_v17_import.sch` is now the current validation-corrected import draft. U5/U6/U7 VCC/GND/OE anchors were rechecked against the upstream KiCad symbol definitions, and R31/R32 pull-ups are restored. `dynamixel_v15_import.sch` is superseded. Real KiCad 9 ERC is still pending.

### Footprints
TPS25947 RPW, BSC009 PG-TDSON-8-7/SuperSO8 and the 8 mm high-current branch net tie have project footprints and structural geometry checks. Real KiCad visual/DRC/stencil review is still required.

### Sensors / Audio / Top level
Architecture contracts and CI exist, but populated native KiCad implementations remain incomplete. Audio passive/reference network recovery is still pending.

## Immediate execution order

1. Regenerate power populated import/native schematic using NTA/NTB/NTC copper net ties; retire `power_v16_import.sch` from active use.
2. Run Dynamixel and power connectivity/structure CI after the validation corrections.
3. In a KiCad 9-capable environment, import/save corrected Dynamixel and power sheets and run real ERC.
4. Recover exact upstream audio codec/amplifier/MEMS passive network.
5. Populate sensors/audio schematics and top-level hierarchy.
6. Freeze XL330/imu_to_dxl connector orientation and mechanical footprint.
7. Freeze board outline/header/mounting holes/connector keepouts.
8. Place high-current corridor and route 4-layer PCB.
9. Run final ERC/DRC, power integrity and 1 Mbps bus bench validation.
10. Generate Gerber/BOM/PnP only after independent pre-fabrication review.

## Fabrication blockers

- `power_v16_import.sch` contains superseded zero-ohm branch-link representation and must not be fabricated
- real KiCad 9 ERC/DRC has not been run
- high-current copper net ties need final PCB-context DRC/thermal/current-path review
- BSC009/TPS25947 visual pad/stencil review incomplete
- XL330/imu_to_dxl connector orientation/polarity not mechanically frozen
- audio populated schematic incomplete
- sensors/top-level native hierarchy incomplete
- PCB placement/routing incomplete
- no Gerber is approved

## Current release status

`v0.17-dev` — validation correction pass completed for the Dynamixel logic and servo branch power split. R31/R32 are restored, U5/U6/U7 anchors are rechecked, generic 0-ohm branch links are removed from the authoritative power contract, and 8 mm copper net ties are now required. **Not fabrication-ready.**
