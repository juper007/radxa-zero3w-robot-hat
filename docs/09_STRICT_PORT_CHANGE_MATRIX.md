# 09 — Upstream-to-Radxa strict-port change matrix

## Baseline

- Upstream: <https://github.com/pollen-robotics/elec_RPI_Robot_HAT>
- Upstream commit: `23eab11927f95ceca0dfa35bf182caeb7db39ea0`
- Upstream board: one 4-layer PCB, 65.00 × 30.90 mm Edge.Cuts-centerline outline (approximately 65 × 31 mm), 127 footprints, 95 electrical nets and 1,021 routed tracks.
- Current port: one 4-layer PCB, same outline, 128 footprints, 95 electrical nets and 1,013 track/via items after the local C45/U9/D1/C22 power correction.
- Port classification: **strict port**, not a redesign.

## Matrix

| Area | Upstream | Radxa strict port | Classification | Status |
|---|---|---|---|---|
| Board count | One HAT | One HAT | Preserved invariant | Applied |
| Outline | 65.00 × 30.90 mm Edge.Cuts centerline | Same routed outline | Preserved invariant | Applied; Radxa collision review pending |
| Header | Raspberry Pi Zero 2×20 physical layout | Radxa ZERO 3W 2×20 on the same physical grid | Host compatibility | Applied |
| J4 SMT/NPTH geometry | 40 pin-passages have 0.02 mm nominal copper clearance | Passage holes and pad outer edges retained; inner land edge relieved 0.20 mm for 0.22 mm nominal clearance | Fabrication correction | DRC-clean candidate; routing unchanged; exact-part/vendor or prototype signoff pending |
| I2C | Pi I2C1 on pins 3/5, BCM `IO_02/03` | RK3566 I2C3 M0 on pins 3/5 | Host compatibility | Net names applied; DT/USB-C PD conflict review pending |
| Dynamixel UART | Pi UART on pins 8/10, BCM `IO_14/15` | RK3566 UART2 M0 on pins 8/10 | Host compatibility | Net names applied; OS console release pending |
| Audio I2S | Pi PCM pins 12/35/38/40 | RK3566 I2S3 M0 on the same pins | Host compatibility | Net names applied; codec clock test pending |
| Logic voltage | 3.3 V GPIO | 3.3 V GPIO, 3.63 V absolute maximum per Radxa documentation | Preserved/verified | Schematic review pending |
| Host 5 V | Header pins 2/4 | Header pins 2/4; USB-C and HAT battery sources are mutually exclusive | Preserved invariant plus operating constraint | Warning applied; reverse-current bench test pending |
| Power topology | 5–28 V input, motor connector may feed the board, AP63205 2 A conversion | Topology retained; C45 10 µF / 50 V X7R local input bypass added; C21/C22 rating metadata corrected | Fabrication/power-integrity correction | DRC-clean; 8 Ω/audio limit/load-step/thermal EVT pending |
| Dynamixel connectors | On-board TTL and RS-485 connectors | Unchanged | Preserved invariant | Applied |
| IMU | On-board BMI088 | Unchanged | Preserved invariant | Applied |
| Audio | On-board codec, microphone and speaker output | Unchanged | Preserved invariant | Applied |
| Main Qwiic | J5 on pins 3/5 I2C | J5 on I2C3 M0 pins 3/5 | Host compatibility | Applied |
| Auxiliary Qwiic | J6/J7/J8 use software-I2C-capable GPIO pairs with 10 kΩ pull-ups | Same routed connectors, 0 Ω links and pull-ups populated; GPIO pairs exposed as `i2c-gpio` aliases 10/11/12 | Functional-parity host adaptation | Hardware and DTBO compile applied; runtime transfer validation pending |
| HAT EEPROM | Pi HAT identification EEPROM | Retained DNP | Raspberry Pi-only feature | Preserved DNP |
| PCB routing | Production-routed upstream board, 1,021 track/via items | Host routes retained; only local U9/D1/C22 power copper changed for C45, producing 1,013 current track/via items | Preserved host routing plus reviewed power correction | Applied; local geometry and filled zone hash-locked |
| Footprint libraries | External/missing `Library_Pollen` and `LCSC_parts_lib`; installed-library D1 mismatch | 12 exact embedded definitions vendored in three project-local `.pretty` libraries with `fp-lib-table` | Manufacturing provenance correction | Applied; PCB byte-identical, DRC 0, manifest/hash guarded |
| Project identity | `elec_RPI_Robot_HAT` | `radxa_zero3w_robot_hat` | Required derivative identity | Applied |
| Daughterboard | None | None | Preserved invariant | Applied |

## Complete host-net rename list

All 18 host-facing net renames are listed below. The first eight select the
active Radxa I2C/UART/I2S functions. The remaining ten replace Raspberry Pi BCM
names with the Radxa ball/function or physical-pin identity. These are semantic
label changes only: component membership and PCB copper connectivity are
unchanged.

| Header pin | Upstream net | Radxa-port net | Role |
|---:|---|---|---|
| 3 | `IO_02` | `I2C3_SDA_M0` | Active I2C3 data |
| 5 | `IO_03` | `I2C3_SCL_M0` | Active I2C3 clock |
| 8 | `IO_14` | `UART2_TX_M0` | Active Dynamixel UART TX |
| 10 | `IO_15` | `UART2_RX_M0` | Active Dynamixel UART RX |
| 11 | NC | `AMP_ENABLE` / GPIO3_A1 | Approved Stage 2 default-OFF amplifier control, active HIGH |
| 12 | `IO_18` | `I2S3_SCLK_M0` | Active audio serial clock |
| 35 | `IO_19` | `I2S3_LRCK_M0` | Active audio frame clock |
| 38 | `IO_20` | `I2S3_SDI_M0` | Active audio input |
| 40 | `IO_21` | `I2S3_SDO_M0` | Active audio output |
| 7 | `IO_04` | `GPIO3_C4_P7` | J6 software-I2C SDA |
| 15 | `IO_22` | `GPIO3_B0_P15` | Radxa GPIO identity |
| 19 | `IO_10` | `GPIO4_C3_P19` | J8 software-I2C SDA |
| 21 | `IO_09` | `GPIO4_C5_P21` | J7 software-I2C SCL |
| 23 | `IO_11` | `GPIO4_C2_P23` | J8 software-I2C SCL |
| 24 | `IO_08` | `GPIO4_C6_P24` | J7 software-I2C SDA |
| 27 | `ID_SD` | `I2C4_SDA_M0_P27` | Upstream HAT-ID path; U4 DNP |
| 28 | `ID_SC` | `I2C4_SCL_M0_P28` | Upstream HAT-ID path; U4 DNP |
| 29 | `IO_05` | `GPIO3_B3_P29` | J6 software-I2C SCL |
| 31 | `IO_06` | `GPIO3_B4_P31` | Populated battery-presence input; Stage 2 Q3 host-referenced collector, connected=LOW; not DNP or voltage ADC |

## Approved corrective exceptions

Approved corrective exceptions retain the single board and all connectors:
Stage 1 changes Q2's gate rating/land, R8 VS bias and C39's rating. Stage 2
replaces D2's battery-clamp function with host-referenced Q3 sensing, changes
R24/R3 values, and adds Q3/Q4/Q5 plus R42–R46 for active-LOW battery presence
and default-OFF amplifier control. D2 is removed **with its function replaced**,
not marked DNP to discard a feature. Every other upstream electrical membership
is checked after reversing only these explicitly approved exceptions.

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

Validation uses KiCad 10.0.6 and regenerates the upstream reports/netlist from the pinned commit in CI. The imported project's exact rule severities, constraints, exclusions and four ERC/seven DRC ignored-check categories are locked by the checker; a green strict-port result establishes regression parity, not fabrication readiness.
