# Dynamixel Upstream Topology Recovery

Status: DESIGNING / evidence-backed recovery  
Date: 2026-09-09

## Goal

Recover the proven half-duplex DYNAMIXEL interface from Pollen Robotics' Apache-2.0 `elec_RPI_Robot_HAT` before translating it to the Radxa-specific V1 sheet. This avoids inventing a direction-control scheme that may not match the proven hardware timing.

## Verified upstream devices

- U5: `74LVC1G08`, SOT-23-5 — receive-path combiner
- U6: `SN74LVC1G125DBV`, SOT-23-5 — active-low-OE TTL receive buffer
- U7: `SN74LVC1G126DBVR`, SOT-23-5 — active-high-OE TTL transmit buffer
- U8: `SIT3088E`, MSOP-8-EP — optional RS-485 path

Production BOM also identifies U5 C7666, U6 C3040625, U7 C7834, U8 C2922535 and R33 = 150 ohm.

## Recovered TTL signal direction

Coordinate/net tracing of the upstream KiCad source corrects an earlier V1 draft assumption. The actual TTL flow is:

```text
IO_14 / host UART TX
        |
        v
 U7 SN74LVC1G126
 active-high OE TX buffer
        |
        v
     DXL_DATA
        |
        v
 U6 SN74LVC1G125
 active-low OE RX buffer
        |
        v
    TTL_RX_OUT
        |
        +----> U5 74LVC1G08 ----> IO_15 / host UART RX
        |           ^
        |           |
        |      optional RS-485 RX source
```

Therefore on Radxa ZERO 3W:

- physical pin 8 / UART2_TX_M0 -> U7 A
- U7 Y -> DXL_DATA
- DXL_DATA -> U6 A
- U6 Y -> TTL receive aggregation
- U5 Y -> physical pin 10 / UART2_RX_M0

This is now reflected in `hardware/kicad/dynamixel_v1_connectivity.csv` and enforced by `check_dynamixel_design.py`.

## Why U5 exists

U5 was previously misidentified as part of the direction generator. Source-coordinate tracing instead places its output directly on the upstream `IO_15` receive path. Its two inputs aggregate receive sources from the TTL and optional RS-485 interfaces. Since idle UART receive lines are high, an AND gate is a practical way for either active receive path to pull the combined RX low while both idle sources remain high.

For a TTL-only optimized V1, U5 could theoretically be removed and U6 Y connected directly to UART2_RX. For now V1 will **retain U5** because:

1. it preserves the upstream-proven architecture;
2. it keeps optional RS-485 compatibility possible;
3. removing it provides negligible BOM/area benefit;
4. keeping it reduces behavioral divergence before hardware validation.

If RS-485 is DNP, its U5 input must have a defined idle-high state and must not float.

## Direction/OE network — still open

The remaining critical recovery item is the exact auto-direction/OE network:

- U6 pin 1 is active-low OE.
- U7 pin 1 is active-high OE.
- upstream includes a `Dynamixel_dir` node and discrete logic/transistor components near that network.
- exact passive/transistor relationships must be recovered before this sheet can enter REVIEW.

Do **not** simply tie U6 and U7 OE together without accounting for opposite polarities. Do not replace the hardware direction function with an arbitrary Radxa GPIO unless evidence from the final hardware/software integration requires it.

## Series resistor

The upstream production BOM contains `R33 = 150 ohm`. It is being retained as the leading source-series candidate for the TTL transmit/data path, but exact coordinate-to-net confirmation remains required before it is marked VERIFIED.

## Current MicroDuck software implication

Current MicroDuck uses `/dev/ttyS2` at 1 Mbps. Its control loop performs a combined DYNAMIXEL sync-read covering all 15 XL330 servos plus the `imu_to_dxl` IMU node. No separate host direction-GPIO operation is exposed by the normal bus API, reinforcing the decision to preserve hardware-managed half-duplex direction behavior.

## IMU implication

The current robot's primary orientation source is the `imu_to_dxl v2` node on DXL_DATA. Consequently the old HAT BMI088 is optional compatibility/diagnostic hardware, not required for the primary control loop.

## RS-485 policy

RS-485 remains optional/DNP in V1. U8 may be retained as a layout option, but its receive output must not interfere with U5 when DNP and the unpopulated path must not load DXL_DATA.

## Implementation constraints

- logic supply is Radxa +3V3;
- no Radxa UART pin may see unsafe 5 V levels;
- preserve TX/RX tri-state turnaround behavior;
- keep DXL_DATA test access;
- reserve low-capacitance ESD protection near off-board connectors;
- servo branch power segmentation A/B/C does not create separate DATA buses;
- all 15 servos and `imu_to_dxl` share one DXL_DATA bus;
- verify connector pin order independently before fabrication.

## Evidence confidence

HIGH / recovered:
- U5/U6/U7 device identities and package family
- U7 A <- host TX
- U7 Y -> DXL_DATA
- U6 A <- DXL_DATA
- U6 Y -> receive aggregation path
- U5 Y -> host RX
- 3.3 V logic domain
- current `/dev/ttyS2` / 1 Mbps MicroDuck bus
- combined servo + `imu_to_dxl` bus architecture

OPEN / fabrication blocker:
- exact U6/U7 OE auto-direction network
- exact second U5 receive input net and DNP bias policy
- final confirmation that R33=150R sits in the intended TTL source-series location
- final connector footprint/orientation

## Licensing

Upstream Pollen hardware is Apache License 2.0. Directly adapted schematic material will retain attribution and a prominent modification notice. Modified source must not be represented as original Pollen production hardware.
