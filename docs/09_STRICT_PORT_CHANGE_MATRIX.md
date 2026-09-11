# 09 — Upstream-to-Radxa strict-port change matrix

## Baseline

- Upstream: <https://github.com/pollen-robotics/elec_RPI_Robot_HAT>
- Upstream commit: `23eab11927f95ceca0dfa35bf182caeb7db39ea0`
- Upstream board: one 4-layer PCB, 65.05 × 30.95 mm, 127 footprints, 95 electrical nets and 1,021 routed tracks.
- Port classification: **strict port**, not a redesign.

## Matrix

| Area | Upstream | Radxa strict port | Classification | Status |
|---|---|---|---|---|
| Board count | One HAT | One HAT | Preserved invariant | Applied |
| Outline | 65.05 × 30.95 mm | Same routed outline | Preserved invariant | Applied; Radxa collision review pending |
| Header | Raspberry Pi Zero 2×20 physical layout | Radxa ZERO 3W 2×20 on the same physical grid | Host compatibility | Applied |
| I2C | Pi I2C1 on pins 3/5, BCM `IO_02/03` | RK3566 I2C3 M0 on pins 3/5 | Host compatibility | Net names applied; DT/USB-C PD conflict review pending |
| Dynamixel UART | Pi UART on pins 8/10, BCM `IO_14/15` | RK3566 UART2 M0 on pins 8/10 | Host compatibility | Net names applied; OS console release pending |
| Audio I2S | Pi PCM pins 12/35/38/40 | RK3566 I2S3 M0 on the same pins | Host compatibility | Net names applied; codec clock test pending |
| Logic voltage | 3.3 V GPIO | 3.3 V GPIO, 3.63 V absolute maximum per Radxa documentation | Preserved/verified | Schematic review pending |
| Host 5 V | Header pins 2/4 | Header pins 2/4 | Preserved invariant | Backfeed review pending |
| Power topology | 5–28 V input, motor connector may feed the board, on-board conversion | Unchanged | Preserved invariant | Applied; target-load review pending |
| Dynamixel connectors | On-board TTL and RS-485 connectors | Unchanged | Preserved invariant | Applied |
| IMU | On-board BMI088 | Unchanged | Preserved invariant | Applied |
| Audio | On-board codec, microphone and speaker output | Unchanged | Preserved invariant | Applied |
| Main Qwiic | J5 on pins 3/5 I2C | J5 on I2C3 M0 pins 3/5 | Host compatibility | Applied |
| Auxiliary Qwiic | J6/J7/J8 use Pi-specific auxiliary I2C/GPIO selections | Retained physically, marked DNP | Verified incompatibility containment | Applied |
| HAT EEPROM | Pi HAT identification EEPROM | Retained DNP | Raspberry Pi-only feature | Preserved DNP |
| PCB routing | Production-routed upstream board | Routing retained; critical net names changed only | Preserved invariant | Applied |
| Project identity | `elec_RPI_Robot_HAT` | `radxa_zero3w_robot_hat` | Required derivative identity | Applied |
| Daughterboard | None | None | Preserved invariant | Applied |

## Explicitly excluded from this port

The following ideas belong only to the archived redesign and are not strict-port requirements:

- 80 × 50 mm power daughterboard;
- 20 A-class three-branch servo distribution redesign;
- LM74700/BSC009 ideal-diode replacement;
- TPS259470A protected Radxa branch;
- nine added bulk-capacitor packages;
- J201/J202 cross-board harnesses.

They remain preserved at `archive/v027-split-hat` / `2f2afd8` and must not be merged into this branch without explicit architecture approval.

## Evidence and limitations

The pin mapping uses Radxa's ZERO 3 hardware-interface documentation and the ZERO 3W product brief. The `i2c3m0_xfer` use on pins 3/5 is also demonstrated by Pollen Robotics' MicroDuck overlay, which documents the conflict with the vendor FUSB302 node on I2C3 M1.

Renaming a net does not by itself validate device-tree ownership, boot-time pin state, analog integrity or mechanical fit. Those remain release gates.
