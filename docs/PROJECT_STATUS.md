# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 power implementation + Phase 2 Dynamixel TTL recovery + Phase 3 sensor architecture started**

## Completed

- [x] Repository initialized and Radxa/MicroDuck architecture documented
- [x] Radxa ZERO 3W 40-pin mapping established
- [x] XL330-M288-T 15-servo current budget completed
- [x] V1 frozen to external regulated 5 V high-current input
- [x] Servo and Radxa current paths separated
- [x] 4-layer / 2 oz outer-copper high-current strategy defined
- [x] Main protection selected: LM74700QDBVRQ1 + BSC009NE2LS5I
- [x] Radxa branch selected: TPS259470ARPWR
- [x] TPS25947 first-pass ILIM/dVdt/OVLO values frozen
- [x] Critical power-device package pin maps independently checked
- [x] Earlier Q1 source/drain orientation error corrected
- [x] Project-local power symbol library added
- [x] Automated power connectivity checker added and GitHub Actions run passed
- [x] Stale 5–28 V/buck POWER_SHEET_SPEC replaced with current 5 V design
- [x] Power BOM synchronized with frozen V1 parts/values
- [x] Power footprint verification gate created; no guessed land pattern may enter fabrication release
- [x] Upstream Pollen DYNAMIXEL logic devices/BOM recovered
- [x] Radxa UART2 physical mapping fixed to pins 8/10
- [x] Current MicroDuck `/dev/ttyS2` 1 Mbps bus architecture confirmed
- [x] Current MicroDuck IMU architecture reclassified: imu_to_dxl shares DYNAMIXEL bus
- [x] On-HAT BMI088 reclassified as optional/compatibility hardware
- [x] DYNAMIXEL V1 connectivity contract and CI checker created
- [x] Earlier DYNAMIXEL U6/U7 direction-role assumption corrected by tracing upstream KiCad coordinates/nets
- [x] Upstream recovered TX path: UART2_TX -> U7 SN74LVC1G126 -> DXL_DATA
- [x] Upstream recovered RX path: DXL_DATA -> U6 SN74LVC1G125 -> U5 receive combiner -> UART2_RX
- [x] U5 reclassified as TTL/optional-RS485 receive combiner, not direction generator
- [x] DYNAMIXEL schematic implementation contract synchronized with corrected roles
- [x] Sensor architecture document created with imu_to_dxl primary and BMI088 optional
- [x] Upstream Apache-2.0 derivative/attribution requirements documented
- [x] Top-level README synchronized with actual V1 architecture

## Key electrical numbers

- XL330 supply: regulated 5 V
- XL330 stall current at 5 V: ~1.47 A each
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa/audio/logic branch target: ~4 A
- development supply: regulated 5 V, 15–20 A class
- TPS259470A current-limit target: ~4.05 A calculated typical
- host startup ramp target: ~9.75 ms
- host OVLO target: ~5.69 V nominal
- DYNAMIXEL: `/dev/ttyS2`, 1 Mbps, Protocol V2
- DYNAMIXEL population target: 15 servos + imu_to_dxl

## Current implementation state

### Power
Architecture and values are frozen at first-pass level. Connectivity sanity checks pass. Exact manufacturer land patterns for TPS25947 RPW and BSC009 SuperSO8 remain fabrication blockers. `power.kicad_sch` is not yet a fully electrically populated sheet, so real KiCad ERC has not run.

### DYNAMIXEL
The major TX/RX role mapping is now recovered from upstream source rather than guessed. U7 is the TX tri-state buffer and U6 is the RX tri-state buffer. U5 combines receive sources and drives host RX. The remaining critical recovery item is the exact automatic OE/direction network driving U6 active-low OE and U7 active-high OE. Until that network is recovered and wired, the sheet remains DESIGNING.

### Sensors
Current MicroDuck primary orientation comes from an external `imu_to_dxl` node sharing DXL_DATA. The legacy BMI088 is optional/DNP compatibility hardware. I2C3 remains allocated for audio codec control, Qwiic/expansion, and optional sensors.

## In progress

- [ ] Finish exact U6/U7 OE auto-direction network recovery from upstream source
- [ ] Confirm U5 optional-RS485 receive input and DNP idle-high bias
- [ ] Confirm R33 150R exact TTL net placement
- [ ] Replace Dynamixel skeleton with electrically populated KiCad sheet
- [ ] Transcribe and independently check TPS25947 RPW manufacturer land pattern
- [ ] Transcribe and independently check BSC009 SuperSO8 land pattern
- [ ] Populate electrically wired `power.kicad_sch`
- [ ] Run actual KiCad 9 ERC
- [ ] Verify/freeze 3-pin XL330 connector footprint and polarity
- [ ] Define audio/mic sheet
- [ ] Build top-level integration sheet

## Immediate execution order

1. Finish OE/direction and R33 upstream trace.
2. Freeze TTL-only DYNAMIXEL circuit and optional RS-485 DNP behavior.
3. Convert DYNAMIXEL skeleton to real symbols/wires.
4. Finish exact high-current power footprints.
5. Convert power skeleton to real symbols/wires.
6. Build audio/mic and I2C expansion sheets.
7. Integrate all sheets around Radxa header.
8. Freeze mechanical outline/header/mounting holes and connector keepouts.
9. Place high-current power and servo connectors first.
10. Place DYNAMIXEL/sensor/audio blocks.
11. Route 4-layer PCB and review current return/noise isolation.
12. Run KiCad ERC/DRC and resolve every unexplained violation.
13. Generate Gerber/BOM/PnP only after independent pre-fab review.

## Fabrication blockers

- TPS25947 and BSC009 exact footprints not yet independently verified
- power electrical KiCad wiring/ERC incomplete
- DYNAMIXEL OE auto-direction network recovery incomplete
- DYNAMIXEL electrical KiCad wiring incomplete
- integrated schematic incomplete
- PCB placement/routing incomplete
- mechanical connector interference review incomplete
- no Gerber is approved

## Current release status

`v0.9-dev` — upstream DYNAMIXEL TX/RX topology corrected and sensor architecture aligned to current MicroDuck. **Not fabrication-ready.**
