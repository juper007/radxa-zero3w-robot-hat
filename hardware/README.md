# Hardware

## Active strict-port design

The active KiCad project is a single-board derivative of Pollen Robotics' `elec_RPI_Robot_HAT` at upstream commit `23eab11927f95ceca0dfa35bf182caeb7db39ea0`.

- `kicad/radxa_zero3w_robot_hat.kicad_pro` — project
- `kicad/radxa_zero3w_robot_hat.kicad_sch` — top-level schematic
- `kicad/radxa_zero3w_robot_hat.kicad_pcb` — routed 65.05 × 30.95 mm PCB
- `kicad/main.kicad_sch` — 40-pin header and board integration
- `kicad/power.kicad_sch` / `pwr_supply_charge.kicad_sch` — unchanged upstream single-board power concept
- `kicad/dynamixel.kicad_sch` — upstream TTL/RS-485 interface and connectors
- `kicad/sensors.kicad_sch` — upstream BMI088 and Qwiic circuitry
- `kicad/audio.kicad_sch` — upstream codec, microphone and speaker circuitry

There is no active power daughterboard. The earlier split design is isolated on `archive/v027-split-hat`.

## Applied host changes

Critical nets retain their upstream physical header pins and routed copper while using Radxa names:

- pins 3/5 — `I2C3_SDA_M0` / `I2C3_SCL_M0`
- pins 8/10 — `UART2_TX_M0` / `UART2_RX_M0`
- pins 12/35/38/40 — `I2S3_SCLK_M0` / `I2S3_LRCK_M0` / `I2S3_SDI_M0` / `I2S3_SDO_M0`

U4 remains DNP. J6/J7/J8 are DNP because their Raspberry Pi auxiliary-I2C routing has not been redesigned for Radxa. J5 remains the primary I2C/Qwiic connector.

## Validation

See `../validation/strict_port/` and `kicad/check_strict_port.py`.

The upstream and adapted designs have identical ERC/DRC/parity finding counts. The inherited 55 ERC warnings, 40 DRC hole-clearance errors, 9 DRC library-footprint warnings and 111 `Datasheet` field parity warnings remain open and prevent fabrication approval.

## Upstream libraries

The KiCad sources embed the symbols and footprints needed to open and validate the design. Some library identifiers and 3D-model paths retain upstream names for traceability and may require local path configuration for complete 3D rendering. Do not replace embedded upstream footprints merely to rename them; verify geometry and production identity first.
