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

The Raspberry Pi HAT EEPROM is retained as upstream DNP. All four upstream Qwiic connectors are populated for functional parity. J5 remains on hardware I2C3 M0 pins 3/5 with the codec and IMU. J6/J7/J8 retain the upstream routed GPIO pairs and are exposed as independent open-drain `i2c-gpio` buses by [`software/overlays/radxa-zero3w-robot-hat-qwiic.dts`](software/overlays/radxa-zero3w-robot-hat-qwiic.dts). Their original 0 Ω links and 10 kΩ pull-ups are populated.

## Software requirement

Using hardware I2C3 M0 on pins 3/5 requires the Radxa device-tree configuration to select `i2c3m0_xfer`. On vendor device trees this can conflict with the FUSB302 USB-C PD controller on I2C3 M1; the software overlay and resulting USB-C behavior must be reviewed before release. The Qwiic parity overlay adds J6/J7/J8 as aliases `i2c10`, `i2c11` and `i2c12`; the intended OS image must enable `CONFIG_I2C_GPIO`, leave those six GPIOs unclaimed, and pass runtime enumeration and transfer tests.

## Source and validation

- Upstream source revision: `23eab11927f95ceca0dfa35bf182caeb7db39ea0`
- KiCad sources: [`hardware/kicad/`](hardware/kicad/)
- Change matrix: [`docs/09_STRICT_PORT_CHANGE_MATRIX.md`](docs/09_STRICT_PORT_CHANGE_MATRIX.md)
- Current status: [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)
- Power review: [`docs/10_POWER_INTEGRITY_REVIEW.md`](docs/10_POWER_INTEGRITY_REVIEW.md)
- Mechanical/RF review: [`docs/11_RADXA_MECHANICAL_REVIEW.md`](docs/11_RADXA_MECHANICAL_REVIEW.md)
- Validation evidence: [`validation/strict_port/`](validation/strict_port/)

The routed board is **not yet approved for fabrication**. KiCad 10.0.6 CI regenerates reports from both the port and pinned upstream commit and locks rule policy, J4, the C45/U9 power region and the filled zone. Current DRC has zero findings and zero unconnected items after project-local footprint vendoring. Remaining gates include J4 supplier/prototype signoff, C45 physical gap, the 2 A load/thermal envelope, single-source backfeed testing, external-antenna/OTA policy, cable access and final manufacturing-package review.

## License and attribution

The active KiCad design is a modified derivative of Pollen Robotics' `elec_RPI_Robot_HAT`, licensed under Apache License 2.0. Upstream authorship and the exact source revision are preserved in the project documentation.
