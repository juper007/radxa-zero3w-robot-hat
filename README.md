# Radxa ZERO 3W Robot HAT

A **strict single-board port** of Pollen Robotics' Apache-2.0 [`elec_RPI_Robot_HAT`](https://github.com/pollen-robotics/elec_RPI_Robot_HAT) for the Radxa ZERO 3W.

## Scope

The active design preserves the upstream product architecture:

- one 65 × 31 mm four-layer HAT PCB;
- the upstream 5–28 V power-input and 5 V conversion concept;
- on-board Dynamixel TTL/RS-485 circuitry and connectors;
- on-board BMI088 IMU, audio codec, MEMS microphone, speaker and expansion connectors;
- the original routed PCB as the layout baseline.

There is **no power daughterboard** in this branch. The earlier split-power redesign is preserved separately on `archive/v027-split-hat` at commit `2f2afd8`.

## Radxa-specific changes

Only host-facing compatibility changes are active:

| Physical pins | Upstream use | Radxa ZERO 3W use |
|---|---|---|
| 3 / 5 | Raspberry Pi I2C1 (`GPIO2/3`) | RK3566 `I2C3_SDA/SCL_M0` |
| 8 / 10 | Raspberry Pi UART (`GPIO14/15`) | RK3566 `UART2_TX/RX_M0` |
| 12 / 35 / 38 / 40 | Raspberry Pi PCM/I2S | RK3566 `I2S3_SCLK/LRCK/SDI/SDO_M0` |
| 2 / 4 | 5 V host rail | Radxa 5 V input pins |
| 1 / 17 | 3.3 V | Radxa 3.3 V rail |

The schematic and PCB net names identify these Radxa functions instead of Raspberry Pi BCM names. The physical routes are retained because the required interfaces occupy the same header pins.

The Raspberry Pi HAT EEPROM is retained as upstream DNP. Extra Qwiic connectors J6/J7/J8 and their isolation/pull-up resistors R18/R19/R20/R21/R34/R35/R38/R39 are DNP because their Raspberry Pi auxiliary-I2C pin choices are not direct Radxa equivalents. Main Qwiic J5 remains on pins 3/5 with the codec and IMU.

## Software requirement

Using hardware I2C3 M0 on pins 3/5 requires the Radxa device-tree configuration to select `i2c3m0_xfer`. On vendor device trees this can conflict with the FUSB302 USB-C PD controller on I2C3 M1; the software overlay and resulting USB-C behavior must be reviewed before release.

## Source and validation

- Upstream source revision: `23eab11927f95ceca0dfa35bf182caeb7db39ea0`
- KiCad sources: [`hardware/kicad/`](hardware/kicad/)
- Change matrix: [`docs/09_STRICT_PORT_CHANGE_MATRIX.md`](docs/09_STRICT_PORT_CHANGE_MATRIX.md)
- Current status: [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)
- Power review: [`docs/10_POWER_INTEGRITY_REVIEW.md`](docs/10_POWER_INTEGRITY_REVIEW.md)
- Mechanical/RF review: [`docs/11_RADXA_MECHANICAL_REVIEW.md`](docs/11_RADXA_MECHANICAL_REVIEW.md)
- Validation evidence: [`validation/strict_port/`](validation/strict_port/)

The routed board is **not yet approved for fabrication**. KiCad 10.0.6 CI regenerates reports from both the port and pinned upstream commit and locks rule policy, J4, the C45/U9 power region and the filled zone. Current DRC has zero errors and 9 inherited library warnings. Remaining gates include J4 supplier/prototype signoff, C45 physical gap, the 2 A load/thermal envelope, single-source backfeed testing, external-antenna/OTA policy, cable access and final manufacturing-library review.

## License and attribution

The active KiCad design is a modified derivative of Pollen Robotics' `elec_RPI_Robot_HAT`, licensed under Apache License 2.0. Upstream authorship and the exact source revision are preserved in the project documentation.
