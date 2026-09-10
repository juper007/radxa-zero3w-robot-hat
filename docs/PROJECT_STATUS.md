# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 - Power implementation + Phase 2 Dynamixel TTL design started**

## Completed

- [x] Repository initialized and architecture documented
- [x] Radxa ZERO 3W 40-pin mapping established
- [x] XL330-M288-T 15-servo current budget completed
- [x] V1 input frozen to regulated 5 V high-current supply
- [x] Servo and Radxa current paths physically separated
- [x] 2 oz outer copper / wide-pour high-current strategy defined
- [x] Main reverse protection selected: LM74700QDBVRQ1 + BSC009NE2LS5I
- [x] Prototype input direction frozen to XT60-class
- [x] Three nominal 5-servo power branches defined
- [x] Radxa branch device frozen to TPS259470ARPWR
- [x] TPS25947 first-pass ILIM/dVdt/OVLO values frozen
- [x] Critical U1/Q1/U2 package pin maps independently re-verified
- [x] Earlier Q1 source/drain orientation error corrected
- [x] Project-local power symbol library and sym-lib-table created
- [x] Automated power connectivity sanity checker added
- [x] GitHub Actions power-design sanity check passed
- [x] Obsolete 5–28 V/buck POWER_SHEET_SPEC completely replaced with current 5 V architecture
- [x] Dynamixel TTL subsystem design document started

## Key electrical numbers

- XL330-M288-T supply: 5 V
- XL330-M288-T stall current at 5 V: ~1.47 A
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa/audio/logic branch target: ~4 A
- Pathological total envelope: ~26 A
- Development supply: regulated 5 V, 15–20 A class
- TPS259470A host current-limit target: ~4.05 A calculated typical
- Host startup ramp target: ~9.75 ms
- Host OVLO target: ~5.69 V nominal
- Dynamixel bus target: UART2, 1 Mbps, 3.3 V host logic

## Verified package pin maps

LM74700QDBVRQ1 DBV: 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE.

BSC009NE2LS5I: pins 1/2/3 SOURCE, pin 4 GATE, pins 5/6/7/8 DRAIN.

TPS259470ARPWR: 1 EN/UVLO, 2 OVLO, 3 AUXOFF, 4 FLT, 5 IN, 6 OUT, 7 DVDT, 8 GND, 9 ILM, 10 ITIMER.

## Current implementation state

Power architecture, values and critical pin maps are at first-pass freeze. `hardware/kicad/POWER_SHEET_SPEC.md` is now synchronized with the regulated-5-V architecture. `power.kicad_sch` is still a structured KiCad source skeleton and must not be treated as fabrication-ready.

Phase 2 has begun in parallel: `docs/06_DYNAMIXEL_TTL_DESIGN.md` defines UART2 pins 8/10, 1 Mbps half-duplex TTL requirements, three servo power groups sharing a logical DATA bus, protection and bring-up criteria.

## In progress

- [ ] Generate manufacturer-verified TPS25947 RPW footprint
- [ ] Generate manufacturer-verified BSC009NE2LS5I SuperSO8 footprint
- [ ] Populate `power.kicad_sch` with actual electrically wired symbols
- [ ] Run actual KiCad 9 ERC
- [ ] Freeze servo connector footprint
- [ ] Recreate/import proven upstream Dynamixel TTL gate circuit
- [ ] Create `hardware/kicad/dynamixel.kicad_sch`
- [ ] Start IMU/I2C sheet after TTL circuit freeze

## Immediate execution order

1. Finish exact power footprints.
2. Finish wired power schematic and ERC.
3. Freeze Dynamixel TTL logic from upstream proven design.
4. Build Dynamixel schematic and connector mapping.
5. Build sensors/I2C sheet.
6. Build audio/mic sheet.
7. Integrate top-level schematic.
8. Build Radxa-size PCB outline and mechanical constraints.
9. Place high-current power and connectors first.
10. Place digital/sensor/audio blocks.
11. Route 4-layer PCB with 2 oz outer copper assumption.
12. Run ERC/DRC and resolve every unexplained violation.
13. Generate BOM/PnP/Gerbers only after final independent review.

## Fabrication blockers

- Exact high-current footprints not yet verified.
- Actual power schematic wiring/ERC not yet complete.
- Dynamixel/sensor/audio sheets not yet integrated.
- PCB placement/routing not yet complete.
- Mechanical interference not yet reviewed.
- No fabrication output is approved yet.

## Current release status

`v0.7-dev` — stale power-sheet architecture corrected and Dynamixel TTL implementation phase started. **Not fabrication-ready.**
