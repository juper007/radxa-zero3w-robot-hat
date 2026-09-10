# Dynamixel Upstream Topology Recovery

Status: DESIGNING / evidence-backed recovery  
Date: 2026-09-09

## Goal

Recover the proven half-duplex DYNAMIXEL interface from Pollen Robotics' Apache-2.0 `elec_RPI_Robot_HAT` before translating it to the Radxa-specific V1 sheet. This avoids inventing a direction-control scheme that may not match the proven hardware timing.

## Verified upstream devices

- U5: `74LVC1G08`, SOT-23-5 — receive-path combiner
- U6: `SN74LVC1G125DBV`, SOT-23-5 — active-low-OE TTL receive buffer
- U7: `SN74LVC1G126DBVR`, SOT-23-5 — active-high-OE TTL transmit buffer
- Q1: `MMBT3906`, SOT-23 — PNP element in automatic direction-generation network
- R26: 10 kΩ, 0402 — direction network
- R27: 10 kΩ, 0402 — direction network
- R28: 20 kΩ, 0402 — direction network
- R33: 150 Ω, 0402 — verified DXL series resistor
- U8: `SIT3088E`, MSOP-8-EP — optional RS-485 path

## Recovered TTL signal direction

The actual upstream TTL flow is:

```text
IO_14 / host UART TX
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
        +----> U5 74LVC1G08 ----> IO_15 / host UART RX
                    ^
                    |
              optional RS-485 RX
```

The local receive tap is on the transceiver side of R33: U7 output and U6 input share `DXL_LOCAL`, then R33 separates that node from the external DXL_DATA wiring.

Therefore on Radxa ZERO 3W:
- physical pin 8 / UART2_TX_M0 -> U7 A
- U7 Y -> DXL_LOCAL
- DXL_LOCAL -> U6 A
- DXL_LOCAL -> R33 pin 1
- R33 pin 2 -> external DXL_DATA
- U6 Y -> TTL receive aggregation
- U5 Y -> physical pin 10 / UART2_RX_M0

## Verified complementary OE control

Source-coordinate tracing proves that U6 pin 1 and U7 pin 1 are on the **same `Dynamixel_dir` net**.

The two buffer types intentionally interpret that same level oppositely:

| Dynamixel_dir | U7 SN74LVC1G126 TX | U6 SN74LVC1G125 RX | Mode |
|---|---|---|---|
| 0 | disabled | enabled | receive |
| 1 | enabled | disabled | transmit |

This removes the need for an inverter between the TX and RX enable controls. It also means tying both OE pins to the same direction net is correct **because** U7 OE is active-high while U6 /OE is active-low.

This truth table is now enforced by `hardware/kicad/check_dynamixel_design.py`.

## Verified R33 placement

R33 is `150R`, footprint 0402, located in the upstream source at schematic coordinate `(201.93, 180.34)` rotated 90 degrees. The generic KiCad `R_Small` symbol has terminals ±2.54 mm from its center; after rotation, R33 endpoints are `(199.39,180.34)` and `(204.47,180.34)`.

The upstream wires prove:
- U7 Y reaches the local bus node through `(189.23,180.34) -> (199.39,180.34)`.
- R33 spans `(199.39,180.34)` to `(204.47,180.34)`.
- The far side continues `(204.47,180.34) -> (209.55,180.34)` toward the connector/protection network.
- U6 A reaches the same local bus node through the `(119.38,140.97) -> (189.23,140.97) -> (189.23,180.34)` trunk.

Therefore R33 is no longer a candidate: it is a **verified series element between DXL_LOCAL and external DXL_DATA**.

## Automatic direction generator — remaining recovery

The remaining source-recovery task is the circuit that generates `Dynamixel_dir` itself.

Verified elements/coordinates so far:
- Q1 `MMBT3906` PNP at `(118.11,68.58)`, mirrored in the upstream schematic.
- R26 `10k` at `(100.33,62.23)`.
- R27 `10k` at `(107.95,68.58)`.
- R28 `20k` at `(120.65,80.01)`.
- `Dynamixel_dir` trunk junction at `(120.65,74.93)`.
- direction trunk continues to both U6 and U7 OE pins.
- source wire from the host-TX corridor reaches `(85.09,68.58) -> (100.33,68.58)`.

The exact Q1 base/emitter/collector-to-resistor wiring and resulting edge behavior still need to be mapped before the electrical KiCad sheet can enter REVIEW.

## Why U5 exists

U5 output is on the upstream `IO_15` receive path. Its inputs aggregate TTL receive and optional RS-485 receive. For a TTL-only optimized V1 U5 could theoretically be removed, but V1 retains it initially to preserve upstream behavior and optional RS-485 compatibility.

If RS-485 is DNP, the unused U5 input must have a defined idle-high state and must not float.

## Current MicroDuck software implication

Current MicroDuck uses `/dev/ttyS2` at 1 Mbps and performs a combined DYNAMIXEL sync-read covering the 15 XL330 servos plus the `imu_to_dxl` IMU node. No normal user-space direction GPIO transaction is required, reinforcing the decision to retain hardware-managed turnaround.

## IMU implication

The current robot's primary orientation source is the `imu_to_dxl` node on DXL_DATA. Consequently the old HAT BMI088 is optional compatibility/diagnostic hardware rather than a primary control-loop requirement.

## RS-485 policy

RS-485 remains optional/DNP in V1. U8 may be retained as a layout option, but its receive output must not interfere with U5 when DNP and the unpopulated path must not load DXL_DATA.

## Implementation constraints

- logic supply is Radxa +3V3;
- no Radxa UART pin may see unsafe 5 V levels;
- preserve the verified complementary OE truth table;
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
- Q1/R26/R27/R28 component identities and placement in direction generator
- 3.3 V logic domain
- current `/dev/ttyS2` / 1 Mbps architecture

OPEN / fabrication blocker:
- exact Q1/R26/R27/R28 automatic-direction generator wiring
- exact second U5 receive input net and DNP bias policy
- final DXL connector footprint/orientation

## Licensing

Upstream Pollen hardware is Apache License 2.0. Directly adapted schematic material will retain attribution and a prominent modification notice. Modified source must not be represented as original Pollen production hardware.
