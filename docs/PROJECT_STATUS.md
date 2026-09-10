# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 power implementation + Phase 2 Dynamixel TTL implementation**

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
- [x] Current MicroDuck IMU architecture reclassified: imu_to_dxl ID 200 shares the DYNAMIXEL bus
- [x] On-HAT BMI088 reclassified as optional/compatibility hardware for current software
- [x] DYNAMIXEL V1 connectivity contract created
- [x] DYNAMIXEL first-pass BOM created
- [x] DYNAMIXEL connectivity sanity checker + GitHub Actions workflow created
- [x] `hardware/kicad/dynamixel.kicad_sch` implementation skeleton created
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
- DYNAMIXEL bus population target: 15 servos + imu_to_dxl ID 200

## Current implementation state

### Power

Architecture and values are frozen at first-pass level. Connectivity sanity checks pass. Exact manufacturer land patterns for the TPS25947 RPW package and BSC009 SuperSO8 remain a fabrication blocker. `power.kicad_sch` is still not fully electrically populated, so actual KiCad ERC has not yet been run.

### DYNAMIXEL

The upstream hardware has been narrowed to U5 `74LVC1G08`, U6 `SN74LVC1G125DBV`, U7 `SN74LVC1G126DBVR` for TTL logic and optional U8 `SIT3088E` for RS-485. Upstream labels `IO_14`, `IO_15` and `Dynamixel_dir` have been recovered. V1 preserves hardware-based direction handling because current MicroDuck opens UART2 as an ordinary serial port and does not require a new host DIR GPIO in the normal API.

The exact Boolean/wire relationship around U5/U6/U7 is still being translated from the upstream KiCad source; corresponding CSV rows are intentionally marked `RECOVERING`/`TO_VERIFY` rather than being guessed.

## In progress

- [ ] Transcribe TI RPW0010A manufacturer land pattern and independently check all pad dimensions
- [ ] Transcribe Infineon SuperSO8/PG-TDSON-8 recommended land pattern and check drain geometry
- [ ] Populate electrically wired `power.kicad_sch`
- [ ] Run actual KiCad 9 ERC on power sheet
- [ ] Finish exact upstream U5/U6/U7 DYNAMIXEL wire/Boolean recovery
- [ ] Replace Dynamixel skeleton with electrically wired KiCad sheet
- [ ] Freeze DXL series resistor and DATA ESD part
- [ ] Freeze actual 3-pin servo connector after cable/mechanical verification
- [ ] Build current-software sensor/expansion strategy with imu_to_dxl primary and optional BMI088
- [ ] Build audio/mic sheet

## Immediate execution order

1. Complete exact DYNAMIXEL U5/U6/U7 source-wire recovery.
2. Convert DYNAMIXEL skeleton to actual electrical schematic.
3. Finish exact high-current power footprints from manufacturer drawings.
4. Finish electrical power sheet.
5. Integrate power + host + DYNAMIXEL at top level.
6. Add Qwiic/I2C and optional legacy BMI088 compatibility.
7. Add audio codec/MEMS mic/speaker circuitry.
8. Freeze 65 x ~31 mm mechanical outline and header/mounting holes.
9. Place high-current connector/fuse/MOSFET/servo connectors first.
10. Place host/DYNAMIXEL/sensors/audio.
11. Route 4-layer PCB, prioritizing high-current return and audio isolation.
12. Run ERC/DRC and resolve every unexplained violation.
13. Generate Gerber/BOM/PnP only after independent pre-fab review.

## Fabrication blockers

- TPS25947 and BSC009 exact footprints not yet independently verified
- power KiCad wiring/ERC incomplete
- exact DYNAMIXEL auto-direction wiring recovery incomplete
- integrated schematic incomplete
- PCB placement/routing incomplete
- mechanical connector interference review incomplete
- no Gerber is approved

## Current release status

`v0.8-dev` — power BOM/spec synchronized, manufacturer-footprint verification gate added, current MicroDuck imu_to_dxl architecture incorporated, and DYNAMIXEL topology/BOM/connectivity/CI implementation started. **Not fabrication-ready.**
