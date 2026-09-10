# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 power implementation + Phase 2 Dynamixel TTL recovery + Phase 3 sensors + Phase 4 audio/top-level integration started**

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
- [x] Power footprint verification gate created
- [x] Upstream Pollen DYNAMIXEL logic devices/BOM recovered
- [x] Radxa UART2 physical mapping fixed to pins 8/10
- [x] Current MicroDuck `/dev/ttyS2` 1 Mbps bus architecture confirmed
- [x] Current MicroDuck IMU architecture aligned to imu_to_dxl on DYNAMIXEL bus
- [x] On-HAT BMI088 reclassified as optional/compatibility hardware
- [x] DYNAMIXEL V1 connectivity contract and CI checker created
- [x] DYNAMIXEL TX/RX role correction recovered from upstream: U7 TX, U6 RX, U5 receive combiner
- [x] Sensor architecture document created
- [x] Sensor/I2C connectivity contract created
- [x] Sensor architecture sanity checker + GitHub Actions workflow created
- [x] `hardware/kicad/sensors.kicad_sch` implementation skeleton created
- [x] Audio architecture document created
- [x] Audio connectivity contract created
- [x] Audio architecture sanity checker + GitHub Actions workflow created
- [x] `hardware/kicad/audio.kicad_sch` implementation skeleton created
- [x] Top-level integration connectivity contract created
- [x] Top-level integration checker + GitHub Actions workflow created
- [x] `hardware/kicad/main.kicad_sch` top-level implementation skeleton created
- [x] Upstream Apache-2.0 derivative/attribution requirements documented
- [x] Top-level README synchronized with current V1 architecture

## Key electrical / interface targets

- XL330 supply: regulated 5 V
- XL330 stall current at 5 V: ~1.47 A each
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa/audio/logic branch target: ~4 A
- development supply: regulated 5 V, 15–20 A class
- TPS259470A host current-limit target: ~4.05 A calculated typical
- host startup ramp target: ~9.75 ms
- host OVLO target: ~5.69 V nominal
- DYNAMIXEL: `/dev/ttyS2`, 1 Mbps, Protocol V2
- DYNAMIXEL population: 15 XL330 + imu_to_dxl
- I2C3: pins 3/5, 3.3 V, 400 kHz design target
- I2S3: pins 12 BCLK, 35 LRCLK, 38 SDI, 40 SDO
- Audio reference codec: TLV320AIC3104IRHBR
- Audio reference amplifier: PAM8406D
- Explicit codec 12 MHz MCLK option retained pending final overlay/clock validation

## Current implementation state

### Power
Architecture, component choices, values and connectivity contracts are frozen at first-pass level. Exact TPS25947 RPW and BSC009 SuperSO8 manufacturer land patterns remain fabrication blockers. `power.kicad_sch` is still a structured source skeleton rather than a fully wired/ERC-checked sheet.

### DYNAMIXEL
Major TX/RX topology is corrected from upstream evidence: `UART2_TX -> U7 SN74LVC1G126 -> DXL_DATA`, and `DXL_DATA -> U6 SN74LVC1G125 -> U5 -> UART2_RX`. Exact U6/U7 OE automatic-direction network and the exact R33 150 ohm placement are still being recovered. The sheet remains DESIGNING until those nets are frozen and electrically wired.

### Sensors
Primary current-MicroDuck IMU is the external `imu_to_dxl` node on DXL_DATA. BMI088 is optional/DNP. A single intentional I2C3 pull-up pair, Qwiic expansion interface, architecture checker, CI workflow and KiCad skeleton now exist.

### Audio
Reference architecture is frozen at block level around TLV320AIC3104 + PAM8406D + MEMS mic + explicit 12 MHz MCLK option. Radxa I2C3/I2S3 interface nets are contractually frozen. Exact codec power/analog/passive network still needs upstream recovery before the audio sheet can reach REVIEW.

### Top level
`top_level_v1_connectivity.csv` now defines all cross-sheet interface invariants and `main.kicad_sch` exists as the integration skeleton. It still needs conversion to real hierarchical sheets, J40 symbol, sheet pins and net wiring.

## In progress

- [ ] Finish exact U6/U7 OE auto-direction network recovery from upstream
- [ ] Confirm U5 optional-RS485 receive input and DNP-safe idle behavior
- [ ] Confirm R33 150 ohm exact net placement
- [ ] Convert Dynamixel skeleton to electrically populated KiCad sheet
- [ ] Transcribe/check TPS25947 RPW manufacturer land pattern
- [ ] Transcribe/check BSC009 SuperSO8 manufacturer land pattern
- [ ] Populate electrically wired `power.kicad_sch`
- [ ] Recover exact TLV320AIC3104/PAM8406D/MEMS passive network
- [ ] Convert sensors/audio skeletons to electrically populated sheets
- [ ] Convert `main.kicad_sch` to real hierarchical integration
- [ ] Verify/freeze 3-pin XL330/imu_to_dxl connector footprint and polarity
- [ ] Freeze board outline/header/mounting holes/connector keepouts
- [ ] Run real KiCad 9 ERC

## Immediate execution order

1. Finish Dynamixel OE/direction and R33 source-wire recovery.
2. Convert DYNAMIXEL sheet to actual symbols/wires.
3. Finish exact high-current power footprints.
4. Convert power sheet to actual symbols/wires.
5. Recover and wire audio reference circuit.
6. Wire I2C/Qwiic optional-sensor sheet.
7. Convert top-level skeleton to hierarchical sheet integration.
8. Freeze mechanical outline/header/mounting holes and connector keepouts.
9. Place high-current input/fuse/MOSFET/servo connector corridor first.
10. Place Radxa protection, DXL logic, sensor and audio blocks.
11. Route 4-layer PCB with high-current/ground/audio constraints.
12. Run KiCad ERC/DRC and resolve every unexplained violation.
13. Generate Gerber/BOM/PnP only after independent pre-fab review.

## Fabrication blockers

- TPS25947 and BSC009 exact footprints not independently verified
- power electrical KiCad wiring/ERC incomplete
- DYNAMIXEL OE auto-direction network recovery incomplete
- DYNAMIXEL electrical KiCad wiring incomplete
- audio analog/power/passive network recovery incomplete
- all current subsystem KiCad files are still implementation skeletons, not ERC-complete circuits
- top-level hierarchical integration incomplete
- PCB placement/routing incomplete
- mechanical connector interference review incomplete
- no Gerber is approved

## Current release status

`v0.10-dev` — sensors, audio and top-level interface contracts/CI/KiCad skeletons added; the project is now structurally prepared for full schematic implementation. **Not fabrication-ready.**
