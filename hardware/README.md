# Hardware

## Active strict-port design

The active KiCad project is a single-board derivative of Pollen Robotics' `elec_RPI_Robot_HAT` at upstream commit `23eab11927f95ceca0dfa35bf182caeb7db39ea0`.

- `kicad/radxa_zero3w_robot_hat.kicad_pro` — project
- `kicad/radxa_zero3w_robot_hat.kicad_sch` — top-level schematic
- `kicad/radxa_zero3w_robot_hat.kicad_pcb` — routed 65.00 × 30.90 mm Edge.Cuts-centerline PCB (approximately 65 × 31 mm)
- `kicad/main.kicad_sch` — 40-pin header and board integration
- `kicad/power.kicad_sch` / `pwr_supply_charge.kicad_sch` — upstream single-board power concept with local C45 input-bypass correction
- `kicad/dynamixel.kicad_sch` — upstream TTL/RS-485 interface and connectors
- `kicad/sensors.kicad_sch` — upstream BMI088 and Qwiic circuitry
- `kicad/audio.kicad_sch` — upstream codec, microphone and speaker circuitry

There is no active power daughterboard. The earlier split design is isolated on `archive/v027-split-hat`.

## Applied host changes

Critical nets retain their upstream physical header pins and routed copper while using Radxa names:

- pins 3/5 — `I2C3_SDA_M0` / `I2C3_SCL_M0`
- pins 8/10 — `UART2_TX_M0` / `UART2_RX_M0`
- pins 12/35/38/40 — `I2S3_SCLK_M0` / `I2S3_LRCK_M0` / `I2S3_SDI_M0` / `I2S3_SDO_M0`

U4 remains DNP. J6/J7/J8 and R18/R19/R20/R21/R34/R35/R38/R39 are DNP so that the unqualified Raspberry Pi auxiliary-I2C options do not pull Radxa GPIOs. J5 remains the primary I2C/Qwiic connector.

## Validation

See `../validation/strict_port/` and `kicad/check_strict_port.py`.

The adapted design has 56 ERC warnings: the 55 upstream findings plus one exact, approved C45 `lib_symbol_mismatch` pending library cleanup. It retains 110 remaining `Datasheet` field parity warnings; one inherited J4 field mismatch was resolved by correcting the manufacturing identity. The 40 inherited J4 hole-clearance errors are eliminated while keeping the connector grid fixed, so current DRC contains only 9 inherited library-footprint warnings and no errors. C45 adds 10 µF / 50 V X7R input bypass; C21/C22 metadata now correctly states 22 µF / 10 V, and the local U9/D1/C22 routing plus filled zone are hash-locked. The current board has 128 footprints and 1,013 track/via items. J4 vendor/prototype approval, C45's ≥4.0 mm PCB gap and ≥0.5 mm residual-clearance gate, the 2 A EVT load/thermal envelope, antenna policy and single-source power rule remain fabrication gates. See `../docs/10_POWER_INTEGRITY_REVIEW.md`.

## Upstream libraries

The KiCad sources embed the symbols and footprints needed to open and validate the design. Some library identifiers and 3D-model paths retain upstream names for traceability and may require local path configuration for complete 3D rendering. Do not replace embedded upstream footprints merely to rename them; verify geometry and production identity first.
