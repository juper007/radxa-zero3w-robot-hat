# 01 — Strict-port requirements

## Product identity

| ID | Requirement | Priority |
|---|---|---|
| SR-001 | Remain a single Radxa ZERO 3W HAT; no daughterboard | Must |
| SR-002 | Preserve the upstream 65 × 31 mm form factor and mounting concept | Must |
| SR-003 | Preserve the upstream routed PCB as the starting point | Must |
| SR-004 | Preserve the upstream power-flow concept unless a verified incompatibility blocks it | Must |
| SR-005 | Preserve Dynamixel TTL/RS-485, IMU, audio and all four upstream Qwiic connectors | Must |

## Host interface

| Physical pin(s) | Required Radxa function |
|---|---|
| 3 / 5 | `I2C3_SDA_M0` / `I2C3_SCL_M0` |
| 8 / 10 | `UART2_TX_M0` / `UART2_RX_M0` |
| 12 / 35 / 38 / 40 | `I2S3_SCLK_M0` / `LRCK_M0` / `SDI_M0` / `SDO_M0` |
| 1 / 17 | 3.3 V |
| 2 / 4 | 5 V |
| 6 / 9 / 14 / 20 / 25 / 30 / 34 / 39 | GND |

- All host-facing GPIO must remain within the Radxa 3.3 V domain.
- Raspberry Pi BCM labels shall not be used as the authoritative signal definition.
- Hardware I2C3 M0 and its FUSB302/I2C3 M1 conflict must be handled in the Radxa device tree and documented for users.
- UART2 console/getty ownership must be disabled before Dynamixel use.
- I2S3 clocking and codec compatibility must be verified on the target OS image.

## Upstream options

- U4, the Raspberry Pi HAT identification EEPROM, remains DNP.
- J5 remains on hardware I2C3 M0 pins 3/5.
- J6/J7/J8 and their 0 Ω/pull-up networks shall be populated and exposed as independent Radxa `i2c-gpio` buses using the preserved routed GPIO pairs.
- The release shall include a compilable device-tree overlay and runtime enumeration/transfer test instructions for all four ports.

## Mechanical and power gates

- Radxa ZERO 3W mounting holes and the 40-pin mating orientation must be checked against an authoritative mechanical drawing.
- USB-C, HDMI, microSD, camera and antenna clearances must be reviewed with the actual stack orientation.
- The upstream 5–28 V input and on-board converter are retained for the strict port.
- Simultaneous USB-C and HAT 5 V power is prohibited until backfeed behavior is verified.
- Motor connector polarity and power-input use must retain upstream behavior unless explicitly changed.

## Verification gates

Before fabrication:

- native KiCad ERC and DRC reviewed with every finding dispositioned;
- no new violations relative to the captured upstream baseline;
- pin-by-pin J4 netlist check passes;
- routed connection count and board outline remain consistent with upstream;
- Radxa mechanical overlay and connector-height review completed;
- BOM/footprints checked against the upstream production package;
- bench test plan approved.
