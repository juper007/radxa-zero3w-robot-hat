# 03 - Radxa ZERO 3W Pin Mapping

## Purpose

This document defines the host-side signal allocation for the Radxa ZERO 3W version of the Robot HAT.

The design rule is to identify every signal by:

1. physical 40-pin header number
2. board-level function
3. RK3566 peripheral/mux role

Do not rely on Raspberry Pi BCM numbering.

The reference-document cross-check against official V1.11/V1.12 schematics,
all 40 current J4 contacts and pinned vendor pinctrl is recorded in
[`15_HOST_PINMUX_REFERENCE_AUDIT.md`](15_HOST_PINMUX_REFERENCE_AUDIT.md).
Actual purchased host revision, complete image DTB and runtime ownership remain
unverified; this is not an assembly or OS signoff.

## Baseline mapping

| Physical pin | Electrical rail / planned function | Project use |
|---:|---|---|
| 1 | 3.3 V | Logic / sensor rail reference |
| 2 | 5 V | Host 5 V supply |
| 3 | I2C3 SDA M0 | Main I2C data |
| 4 | 5 V | Host 5 V supply |
| 5 | I2C3 SCL M0 | Main I2C clock |
| 6 | GND | Ground |
| 7 | GPIO3_C4 | J6 SDA through populated R18; R20 pull-up; `i2c10` |
| 8 | UART2 TX M0 | Dynamixel UART TX |
| 9 | GND | Ground |
| 10 | UART2 RX M0 | Dynamixel UART RX |
| 11 | GPIO3_A1 | AMP_ENABLE, active HIGH; LOW/unclaimed requests hardware shutdown |
| 12 | I2S3 SCLK/BCLK M0 | Audio bit clock |
| 14 | GND | Ground |
| 15 | GPIO3_B0 | U11 INT1 through populated R25; not a spare GPIO output |
| 17 | 3.3 V | Logic / sensor rail reference |
| 19 | GPIO4_C3 | J8 SDA; R38 pull-up; `i2c12` |
| 20 | GND | Ground |
| 21 | GPIO4_C5 | J7 SCL; R35 pull-up; `i2c11` |
| 23 | GPIO4_C2 | J8 SCL; R39 pull-up; `i2c12` |
| 24 | GPIO4_C6 | J7 SDA; R34 pull-up; `i2c11` |
| 25 | GND | Ground |
| 27 | I2C4 SDA M0 | HAT-ID path; U4 DNP |
| 28 | I2C4 SCL M0 | HAT-ID path; U4 DNP |
| 29 | GPIO3_B3 | J6 SCL through populated R19; R21 pull-up; `i2c10` |
| 30 | GND | Ground |
| 31 | GPIO3_B4 | Battery presence input: connected=LOW; Q3 collector with R43 pull-up to host 3.3 V; not an ADC |
| 34 | GND | Ground |
| 35 | I2S3 LRCK M0 | Audio frame/LR clock |
| 38 | I2S3 SDI M0 | Codec/mic data to host |
| 39 | GND | Ground |
| 40 | I2S3 SDO M0 | Host audio data to codec |

Physical pins 13, 16, 18, 22, 26, 32, 33, 36 and 37 remain explicitly unconnected. Stage 2 assigns pin 11 to AMP_ENABLE; do not assign a second GPIO owner. Pin 31 was already a populated battery-sense path, not an unused/DNP option; its active-LOW replacement separates the battery resistor/base node from the host-referenced collector. The preserved Qwiic nets on pins 7/29, 24/21 and 19/23 are populated and claimed as the independent `i2c10`, `i2c11` and `i2c12` GPIO-I2C buses.

## I2C3

Planned bus:

- Pin 3: SDA
- Pin 5: SCL
- 3.3 V logic

Expected loads may include:

- IMU
- audio codec control interface
- Qwiic connector J5
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

The existing HAT Y1 12 MHz oscillator drives U2 MCLK directly; J4 pin 13 is
unconnected. The pinned audio overlay describes that physical 12 MHz source
separately from the CPU DAI's 12.288 MHz system clock and makes the CPU DAI
bit/frame master. Actual codec PLL, clock frequencies and capture/playback
still require validation on the intended image; see the reference audit.

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
- Pollen MicroDuck I2C3 HAT overlay reference: https://github.com/pollen-robotics/microduck/blob/6507d2e960417aaa4ecd38eccf59b2dcf586ecd2/deploy/audio/i2c3-pihat.dts
