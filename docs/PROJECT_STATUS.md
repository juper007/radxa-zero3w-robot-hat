# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 power implementation + Phase 2 Dynamixel TTL implementation + Phase 3 sensors + Phase 4 audio/top-level integration**

## Completed

- [x] Repository initialized and Radxa/MicroDuck architecture documented
- [x] Radxa ZERO 3W 40-pin mapping established
- [x] XL330-M288-T 15-servo current budget completed
- [x] V1 frozen to external regulated 5 V high-current input; no onboard high-power buck
- [x] Servo and Radxa current paths separated
- [x] 4-layer / 2 oz outer-copper high-current strategy defined
- [x] Main protection selected: LM74700QDBVRQ1 + BSC009NE2LS5I
- [x] Radxa branch selected: TPS259470ARPWR
- [x] TPS25947 first-pass ILIM/dVdt/OVLO values frozen
- [x] Critical power-device package pin maps independently checked
- [x] Q1 ideal-diode source/drain orientation corrected
- [x] BSC009 package identification corrected to manufacturer-supported `PG-TDSON-8 / SuperSO8`
- [x] TPS25947 RPW and BSC009 SuperSO8 project footprints created and covered by geometry regression checks
- [x] Project-local power symbol and footprint libraries registered
- [x] Power connectivity contract/checker/BOM synchronized
- [x] Populated power legacy-import schematic `power_v16_import.sch` created with LM74700, BSC009, TPS259470A, support passives, servo rails and Radxa power interface
- [x] Power import schematic pin-anchor regression checker added
- [x] Power design Actions run #3 passed after fixing a checker false-positive; connectivity and populated-schematic structure both pass
- [x] Upstream Pollen DYNAMIXEL TX/RX topology recovered: U7 TX, U6 RX, U5 receive combiner
- [x] U6/U7 OE pins proven to share `Dynamixel_dir`; complementary RX/TX truth table frozen
- [x] R33 = 150 ohm proven inline between `DXL_LOCAL` and external `DXL_DATA`
- [x] Q1/R26/R27/R28 automatic direction generator fully recovered
- [x] TTL-only V1 U5 optional-RS485 input frozen with 10k pull-up to +3V3
- [x] DYNAMIXEL connectivity contract/checker/BOM synchronized
- [x] Populated Dynamixel legacy-import schematic `dynamixel_v15_import.sch` created with logic, auto-direction network, R33 and four DXL connectors
- [x] Dynamixel standard-symbol pin anchors corrected and guarded by CI
- [x] DYNAMIXEL Actions run #10 passed for connectivity plus populated-import schematic structure
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
- BSC009 package: PG-TDSON-8 / SuperSO8
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
The electrical contract is now represented by a populated KiCad legacy-import draft, not just notes. `power_v16_import.sch` contains the frozen ideal-diode path, TPS259470A host eFuse network, bulk/decoupling components, three segmented servo rails and a Radxa power interface. Custom-symbol and connector pin anchors are regression-checked and structure CI passes. The native `power.kicad_sch` remains the older skeleton until the import draft is opened/saved in KiCad 9. Real KiCad ERC/DRC has not run.

### DYNAMIXEL
The TTL half-duplex architecture, R33 placement, automatic direction circuit and TTL-only RS-485 DNP behavior are frozen. `dynamixel_v15_import.sch` is populated with the actual logic/passive/connector circuit and has pin-anchor structure CI coverage. The native `dynamixel.kicad_sch` remains a skeleton until KiCad 9 import/save. Real ERC is still pending. XL330/imu_to_dxl connector mechanical orientation remains provisional.

### Footprints
TPS25947 RPW and BSC009 SuperSO8 footprints exist and pass project geometry regression checks. These checks are not a substitute for KiCad visual review, paste/stencil review or board-level DRC. The BSC009 footprint remains pre-fabrication-review gated.

### Sensors
Primary current-MicroDuck IMU is external `imu_to_dxl` on DXL_DATA. BMI088 remains optional/DNP. I2C3/Qwiic contracts and CI exist; actual populated schematic implementation remains to be done.

### Audio
Block-level architecture and Radxa digital interface are frozen. Exact TLV320AIC3104/PAM8406D/MEMS mic power/analog/passive network still requires upstream recovery before a populated import schematic is generated.

### Top level
Cross-sheet interface invariants exist. `main.kicad_sch` is still a structural skeleton and needs real hierarchical sheets, J40 symbol, sheet pins and electrical wiring.

## Immediate execution order

1. Recover exact upstream audio codec/amplifier/MEMS passive network and create a populated audio import schematic.
2. Create populated I2C/Qwiic sensor import schematic with optional BMI088 DNP policy.
3. Create a top-level hierarchical integration draft tying power/DXL/sensors/audio to Radxa J40.
4. In a KiCad 9-capable environment, import/save `dynamixel_v15_import.sch` and `power_v16_import.sch` as native `.kicad_sch` files and run ERC.
5. Resolve all ERC findings; visually review BSC009/TPS25947 footprints and stencil apertures.
6. Freeze board outline/header/mounting holes/connector keepouts.
7. Place high-current power corridor first, then Radxa/DXL/sensor/audio blocks.
8. Route the 4-layer PCB with high-current return and audio isolation constraints.
9. Run KiCad ERC/DRC and resolve every unexplained violation.
10. Generate Gerber/BOM/PnP only after independent pre-fabrication review.

## Fabrication blockers

- native KiCad 9 import/save and real ERC for power/DYNAMIXEL not yet performed
- BSC009/TPS25947 visual pad/stencil/board-level DRC review incomplete
- XL330/imu_to_dxl connector footprint orientation and polarity not mechanically frozen
- audio analog/power/passive recovery incomplete
- sensors populated schematic incomplete
- top-level hierarchical integration incomplete
- PCB placement/routing incomplete
- mechanical connector interference review incomplete
- no Gerber is approved

## Current release status

`v0.16-dev` — populated, pin-anchor-checked import schematics now exist for both DYNAMIXEL and power, and their connectivity/structure CI checks pass. Native KiCad 9 conversion and real ERC/DRC remain mandatory before fabrication. **Not fabrication-ready.**
