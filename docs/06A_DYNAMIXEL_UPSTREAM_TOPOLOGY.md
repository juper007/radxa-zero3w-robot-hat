# Dynamixel Upstream Topology Recovery

Status: RECOVERED / implementation pending  
Date: 2026-09-09

## Goal

Recover the proven half-duplex DYNAMIXEL interface from Pollen Robotics' Apache-2.0 `elec_RPI_Robot_HAT` before translating it to the Radxa-specific V1 sheet. This avoids inventing a direction-control scheme that may not match the proven hardware timing.

## Verified upstream devices

- U5: `74LVC1G08`, SOT-23-5 — receive-path combiner
- U6: `SN74LVC1G125DBV`, SOT-23-5 — active-low-OE TTL receive buffer
- U7: `SN74LVC1G126DBVR`, SOT-23-5 — active-high-OE TTL transmit buffer
- Q1: `MMBT3906`, SOT-23 — PNP element in automatic direction-generation network
- R26: 10 kΩ, 0402 — UART TX direction-sense pull-up
- R27: 10 kΩ, 0402 — Q1 base resistor
- R28: 20 kΩ, 0402 — `Dynamixel_dir` pull-down
- R33: 150 Ω, 0402 — verified DXL series resistor
- U8: `SIT3088E`, MSOP-8-EP — optional RS-485 path

## Recovered TTL signal direction

```text
UART2_TX
   |
   v
U7 SN74LVC1G126
active-high OE TX buffer
   |
   v
DXL_LOCAL
   |
 R33 150R
   |
   v
DXL_DATA ------------------> off-board servos / imu_to_dxl
   ^
   |
DXL_LOCAL
   |
U6 SN74LVC1G125
active-low OE RX buffer
   |
   v
TTL_RX_OUT
   |
   +----> U5 74LVC1G08 ----> UART2_RX
                    ^
                    |
              optional RS-485 RX
```

The local receive tap is on the transceiver side of R33: U7 output and U6 input share `DXL_LOCAL`, then R33 separates that node from external `DXL_DATA`.

Radxa ZERO 3W mapping:
- physical pin 8 / UART2_TX_M0 -> U7 A and automatic-direction sensing network
- U7 Y -> DXL_LOCAL
- DXL_LOCAL -> U6 A
- DXL_LOCAL -> R33 pin 1
- R33 pin 2 -> external DXL_DATA
- U6 Y -> TTL receive aggregation
- U5 Y -> physical pin 10 / UART2_RX_M0

## Verified complementary OE control

U6 pin 1 and U7 pin 1 are on the same `Dynamixel_dir` net.

| Dynamixel_dir | U7 SN74LVC1G126 TX | U6 SN74LVC1G125 RX | Mode |
|---|---|---|---|
| 0 | disabled | enabled | receive |
| 1 | enabled | disabled | transmit |

The opposite OE polarities intentionally provide complementary TX/RX switching without an extra inverter.

## Fully recovered automatic direction generator

The upstream circuit derives `Dynamixel_dir` directly from UART TX; no host direction GPIO is required.

```text
                    +3V3
                      |
          +-----------+-----------+
          |                       |
       R26 10k                 Q1 emitter
          |                   MMBT3906 PNP
          +---- UART2_TX --------- base path
          |          |
          |        R27 10k
          |          |
          +----------+----> Q1 base
                              |
                         Q1 collector
                              |
                       Dynamixel_dir
                              |
                           R28 20k
                              |
                             GND
```

Electrical interpretation:
- R26 = 10 kΩ pulls the UART TX direction-sense node toward +3V3.
- R27 = 10 kΩ limits Q1 base current between UART TX and the PNP base.
- Q1 emitter is tied to +3V3.
- Q1 collector drives `Dynamixel_dir`.
- R28 = 20 kΩ pulls `Dynamixel_dir` to GND when Q1 is off.

### Direction behavior

UART is idle-high. With TX high, Q1 base is approximately at its emitter potential, so Q1 is off and R28 pulls `Dynamixel_dir` low. This selects receive mode: U7 disabled, U6 enabled.

When UART TX goes low, base current flows through R27, Q1 turns on, and its collector raises `Dynamixel_dir`. This enables U7 and disables U6 while the low transmit bit is driven onto DXL_LOCAL/DXL_DATA.

Because UART data is idle-high and the DYNAMIXEL TTL bus is also idle-high, the hardware automatically releases back to receive mode as TX returns high. This preserves the upstream hardware-managed turnaround and avoids software timing dependence on a direction GPIO.

## Verified R33 placement

R33 is `150R`, footprint 0402, at upstream schematic coordinate `(201.93, 180.34)`. Source wiring establishes:
- U7 Y and U6 A share the local node `DXL_LOCAL`.
- R33 pin 1 connects to DXL_LOCAL.
- R33 pin 2 connects to external DXL_DATA.

R33 is therefore a verified series element between the local logic node and off-board bus.

## Why U5 exists

U5 output is on the upstream host RX path. Its inputs aggregate TTL receive and optional RS-485 receive. V1 retains U5 to preserve upstream behavior and keep the RS-485 layout option available.

The remaining RS-485-specific implementation check is to ensure that when U8 is DNP, U5's second input has a deterministic idle-high state rather than floating.

## Current MicroDuck software implication

Current MicroDuck uses `/dev/ttyS2` at 1 Mbps and performs a combined DYNAMIXEL sync-read across the 15 XL330 servos plus the `imu_to_dxl` node. The recovered direction circuit is hardware-managed and therefore does not require a separate normal user-space direction-GPIO transaction.

## IMU implication

The current robot's primary orientation source is the `imu_to_dxl` node on DXL_DATA. The old HAT BMI088 is optional compatibility/diagnostic hardware rather than a primary control-loop requirement.

## RS-485 policy

RS-485 remains optional/DNP in V1. U8 may be retained as a layout option, but its receive output must not interfere with U5 when DNP and the unpopulated path must not load DXL_DATA.

## Implementation constraints

- logic supply is Radxa +3V3;
- no Radxa UART pin may see unsafe 5 V levels;
- preserve the recovered R26/R27/Q1/R28 automatic-direction network;
- preserve the complementary shared-OE truth table;
- preserve R33 = 150 Ω between DXL_LOCAL and external DXL_DATA unless bench signal-integrity testing justifies a value change;
- keep DXL_DATA test access;
- reserve low-capacitance ESD protection near off-board connectors;
- servo power segmentation A/B/C does not create separate DATA buses;
- all 15 servos and `imu_to_dxl` share one DXL_DATA bus;
- verify connector pin order independently before fabrication.

## Evidence confidence

HIGH / recovered:
- U5/U6/U7 identities and roles
- U7 A <- host TX
- U7 Y -> DXL_LOCAL
- U6 A <- DXL_LOCAL
- U6 Y -> receive aggregation
- U5 Y -> host RX
- shared `Dynamixel_dir` on U6/U7 OE
- complementary OE truth table
- R33 150 Ω exact inline placement
- Q1/R26/R27/R28 exact automatic-direction topology
- receive-default / transmit-low behavior of direction generator
- 3.3 V logic domain
- current `/dev/ttyS2` / 1 Mbps architecture

OPEN / fabrication blocker:
- exact second U5 receive input / optional RS-485 DNP-safe bias
- final DXL connector footprint/orientation
- conversion of this recovered topology to a real KiCad electrical sheet
- real KiCad ERC/DRC

## Licensing

Upstream Pollen hardware is Apache License 2.0. Directly adapted schematic material will retain attribution and a prominent modification notice. Modified source must not be represented as original Pollen production hardware.
