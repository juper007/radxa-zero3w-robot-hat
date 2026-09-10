# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 power implementation + Phase 2 Dynamixel TTL implementation + Phase 3 sensors + Phase 4 audio/top-level integration**

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
- [x] Q1 ideal-diode source/drain orientation corrected
- [x] BSC009 package identification corrected to manufacturer-supported `PG-TDSON-8 / SuperSO8`; unsupported dash-variant assumptions removed
- [x] BSC009 manufacturer boardpad/stencil dimensions captured into implementation gate/spec
- [x] TPS25947 RPW footprint transcription + geometry regression checker added
- [x] Project-local power symbol library added
- [x] Automated power connectivity checker added and CI passed
- [x] Stale 5–28 V/buck POWER_SHEET_SPEC replaced with regulated-5-V architecture
- [x] Power BOM synchronized with V1 parts/values
- [x] Upstream Pollen DYNAMIXEL TX/RX topology recovered: U7 TX, U6 RX, U5 receive combiner
- [x] U6/U7 OE pins proven to share `Dynamixel_dir`
- [x] Complementary OE truth table proven: dir=0 RX, dir=1 TX
- [x] R33 = 150 ohm proven inline between `DXL_LOCAL` and external `DXL_DATA`
- [x] Q1/R26/R27/R28 automatic direction generator fully recovered
- [x] Direction behavior locked: UART TX idle-high -> receive; TX-low -> transmit-low
- [x] TTL-only V1 U5 optional-RS485 input behavior frozen: 10k pull-up to +3V3 makes U5 transparent when U8 is DNP
- [x] DYNAMIXEL connectivity contract/checker/BOM synchronized with recovered/frozen topology
- [x] DYNAMIXEL direction-regression GitHub Actions check passed
- [x] Electrically explicit DYNAMIXEL implementation specification added
- [x] Current MicroDuck `/dev/ttyS2` 1 Mbps + imu_to_dxl architecture incorporated
- [x] BMI088 reclassified optional/DNP
- [x] Sensor/I2C architecture, connectivity checker, CI and KiCad skeleton created
- [x] Audio architecture, connectivity checker, CI and KiCad skeleton created
- [x] Top-level integration contract/checker/CI and KiCad skeleton created
- [x] Upstream Apache-2.0 attribution requirements documented

## Key electrical / interface targets

- XL330 supply: regulated 5 V
- XL330 stall current: ~1.47 A each at 5 V
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- development supply: regulated 5 V, 15–20 A class
- TPS259470A host current-limit target: ~4.05 A calculated typical
- host startup ramp target: ~9.75 ms
- host OVLO target: ~5.69 V nominal
- DYNAMIXEL: `/dev/ttyS2`, 1 Mbps, Protocol V2
- DYNAMIXEL population: 15 XL330 + imu_to_dxl
- DXL direction: `Dynamixel_dir=0` receive; `Dynamixel_dir=1` transmit
- DXL automatic direction: Q1 MMBT3906 + R26 10k + R27 10k + R28 20k
- DXL external series resistor: R33 = 150 ohm
- U5 optional-RS485 input in TTL-only V1: 10k pull-up to +3V3
- I2C3: pins 3/5, 3.3 V, 400 kHz target
- I2S3: pins 12 BCLK, 35 LRCLK, 38 SDI, 40 SDO
- Audio: TLV320AIC3104IRHBR + PAM8406D + MEMS mic, 12 MHz MCLK option retained

## Current implementation state

### Power
Electrical topology and first-pass values are frozen. TPS25947 RPW footprint exists and is regression-checked. The BSC009 footprint authority is now corrected to the product-specific Infineon PG-TDSON-8 / SuperSO8 boardpad drawing; unsupported `-46` and `-7` assertions have been removed. The exact copper/paste footprint still must be transcribed and visually reviewed. `power.kicad_sch` remains a source skeleton rather than a final wired/ERC-checked sheet.

### DYNAMIXEL
The TTL half-duplex architecture, R33 placement and automatic direction circuit are source-recovered and CI-locked. The optional RS-485 input behavior is now also frozen for the TTL-only V1: U8 is DNP and U5 input B is pulled high through 10k, so U5 passes TTL_RX_OUT without a floating input. The remaining work is physical connector orientation, actual symbol/wire instantiation and KiCad ERC.

### Sensors
Primary current-MicroDuck IMU is external `imu_to_dxl` on DXL_DATA. BMI088 remains optional/DNP. I2C3/Qwiic contracts and CI exist; actual KiCad wiring remains to be populated.

### Audio
Block-level architecture and Radxa digital interface are frozen. Exact TLV320AIC3104/PAM8406D/MEMS mic power/analog/passive network still requires upstream recovery.

### Top level
Cross-sheet interface invariants exist. `main.kicad_sch` still needs conversion from implementation contract to real hierarchical sheets, J40 symbol, sheet pins and electrical wiring.

## In progress

- [ ] Convert DYNAMIXEL skeleton to electrically populated KiCad sheet
- [ ] Transcribe exact BSC009 PG-TDSON-8 manufacturer land pattern and add CI checks
- [ ] Populate electrically wired `power.kicad_sch`
- [ ] Recover exact TLV320AIC3104/PAM8406D/MEMS passive network
- [ ] Convert sensors/audio skeletons to electrically populated sheets
- [ ] Convert `main.kicad_sch` to real hierarchical integration
- [ ] Verify/freeze 3-pin XL330/imu_to_dxl connector footprint and polarity
- [ ] Freeze board outline/header/mounting holes/connector keepouts
- [ ] Run real KiCad 9 ERC/DRC in a capable environment

## Immediate execution order

1. Convert DYNAMIXEL sheet to actual symbols/wires using the frozen V1 implementation contract.
2. Build and independently verify the BSC009 manufacturer PG-TDSON-8 footprint; extend geometry CI.
3. Convert power sheet to actual symbols/wires.
4. Recover and wire audio reference circuit.
5. Wire I2C/Qwiic optional-sensor sheet.
6. Convert top-level skeleton to hierarchical integration.
7. Freeze mechanical outline/header/mounting holes and connector keepouts.
8. Place high-current power corridor first, then Radxa/DXL/sensor/audio blocks.
9. Route 4-layer PCB with high-current return and audio isolation constraints.
10. Run KiCad ERC/DRC and resolve every unexplained violation.
11. Generate Gerber/BOM/PnP only after independent pre-fabrication review.

## Fabrication blockers

- BSC009 exact product-specific footprint not yet independently checked
- power electrical KiCad wiring/ERC incomplete
- DYNAMIXEL electrical KiCad wiring incomplete
- audio analog/power/passive recovery incomplete
- top-level hierarchical integration incomplete
- PCB placement/routing incomplete
- mechanical connector interference review incomplete
- no Gerber is approved

## Current release status

`v0.13-dev` — unsupported BSC009 dash-variant claims removed; manufacturer PG-TDSON-8/SuperSO8 boardpad authority locked. DYNAMIXEL TTL-only RS-485 DNP behavior is now frozen with a 10k idle-high U5 bias and enforced in the connectivity checker/BOM. **Not fabrication-ready.**
