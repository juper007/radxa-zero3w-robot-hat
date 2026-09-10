# 03 - Radxa ZERO 3W Pin Mapping

## Purpose

This document defines the host-side signal allocation for the Radxa ZERO 3W version of the Robot HAT.

The design rule is to identify every signal by:

1. physical 40-pin header number
2. board-level function
3. RK3566 peripheral/mux role

Do not rely on Raspberry Pi BCM numbering.

## Baseline mapping

| Physical pin | Electrical rail / planned function | Project use |
|---:|---|---|
| 1 | 3.3 V | Logic / sensor rail reference |
| 2 | 5 V | Host 5 V supply |
| 3 | I2C3 SDA M0 | Main I2C data |
| 4 | 5 V | Host 5 V supply |
| 5 | I2C3 SCL M0 | Main I2C clock |
| 6 | GND | Ground |
| 8 | UART2 TX M0 | Dynamixel UART TX |
| 9 | GND | Ground |
| 10 | UART2 RX M0 | Dynamixel UART RX |
| 12 | I2S3 SCLK/BCLK M0 | Audio bit clock |
| 14 | GND | Ground |
| 17 | 3.3 V | Logic / sensor rail reference |
| 20 | GND | Ground |
| 25 | GND | Ground |
| 30 | GND | Ground |
| 34 | GND | Ground |
| 35 | I2S3 LRCK M0 | Audio frame/LR clock |
| 38 | I2S3 SDI M0 | Codec/mic data to host |
| 39 | GND | Ground |
| 40 | I2S3 SDO M0 | Host audio data to codec |

Unused pins remain uncommitted until the detailed schematic assigns enable, interrupt, status or expansion functions.

## I2C3

Planned bus:

- Pin 3: SDA
- Pin 5: SCL
- 3.3 V logic

Expected loads may include:

- IMU
- audio codec control interface
- Qwiic connector(s)
- optional ToF or other external sensors

### I2C design checks

Before release:

- confirm every device address
- confirm total bus capacitance is reasonable
- calculate effective parallel pull-up resistance
- avoid duplicate strong pull-ups on external expansion boards
- verify all devices are 3.3 V-compatible

## UART2

Planned bus:

- Pin 8: TX
- Pin 10: RX

Primary purpose:

- Dynamixel half-duplex TTL bus

### Important software constraint

UART2 may be used as a console/debug UART by the Radxa software stack. The host configuration must disable console/getty ownership before Dynamixel use and enable the intended UART pinmux.

Do not treat UART2 as electrically available merely because the pins exist; host configuration is part of board bring-up.

## I2S3

Planned audio signals:

- Pin 12: BCLK/SCLK
- Pin 35: LRCLK
- Pin 38: SDI into host
- Pin 40: SDO from host

The exact codec clocking topology must be finalized during the audio-design phase, including MCLK requirements and whether an external oscillator/clock source is needed.

## Power pins

### 5 V

Physical pins 2 and 4 are planned as the regulated host-supply connection.

Critical checks:

- verify whether both are tied together on the Radxa board
- calculate connector/contact current margin
- ensure HAT regulator startup does not violate host requirements
- prevent unwanted backfeed when USB power is simultaneously connected

### 3.3 V

Physical pins 1 and 17 are used as host logic reference / low-power rail only after current-source/sink behavior is verified.

The main robot board shall not assume unlimited current is available from this rail.

## Ground

Use multiple 40-pin ground contacts and a continuous ground plane. High-current motor return shall enter the board in a way that minimizes shared impedance with:

- IMU ground
- codec analog ground/reference
- I2C signal return
- UART signal return

## Pin-mapping release checklist

Before schematic freeze, verify all of the following against the current Radxa ZERO 3W documentation and device tree:

- [ ] physical pin number
- [ ] voltage domain
- [ ] mux function
- [ ] Linux device assignment
- [ ] boot-time default state
- [ ] internal pull state
- [ ] conflict with console/debug functions
- [ ] conflict with other selected peripherals
- [ ] safe behavior before Linux configures the pin

## References

- Radxa ZERO 3W hardware documentation: https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface
- Pollen MicroDuck I2C3 HAT overlay reference: https://github.com/pollen-robotics/microduck/blob/main/deploy/audio/i2c3-pihat.dts
