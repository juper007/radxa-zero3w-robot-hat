# DYNAMIXEL_SHEET_IMPLEMENTATION_SPEC

Status: IMPLEMENTATION READY / ERC PENDING  
Target: KiCad 9, Radxa ZERO 3W Robot HAT V1

## Purpose

This file is the electrically explicit source-of-truth for converting `dynamixel.kicad_sch` from a text/skeleton contract into a real wired KiCad sheet.

## Required sheet nets

- `+3V3`
- `GND`
- `UART2_TX`
- `UART2_RX`
- `UART2_TX_DIR_SENSE`
- `Q1_BASE`
- `Dynamixel_dir`
- `DXL_LOCAL`
- `DXL_DATA`
- `TTL_RX_OUT`
- `RS485_RX_OUT`
- `+5V_SERVO_A`
- `+5V_SERVO_B`
- `+5V_SERVO_C`

## Radxa interface

- J40 physical pin 8 -> `UART2_TX`
- J40 physical pin 10 <- `UART2_RX`
- J40 physical pin 17 -> `+3V3`
- ground from multiple J40 ground pins -> `GND`

Do not use Raspberry Pi BCM numbering in schematic labels.

## Automatic direction generator

Populate exactly:

- Q1: MMBT3906 PNP, SOT-23
  - pin 1 B -> `Q1_BASE`
  - pin 2 E -> `+3V3`
  - pin 3 C -> `Dynamixel_dir`
- R26: 10k, 0402
  - one side -> `+3V3`
  - other side -> `UART2_TX_DIR_SENSE`
- R27: 10k, 0402
  - one side -> `UART2_TX_DIR_SENSE`
  - other side -> `Q1_BASE`
- R28: 20k, 0402
  - one side -> `Dynamixel_dir`
  - other side -> `GND`
- `UART2_TX` must connect to `UART2_TX_DIR_SENSE` at the sensing junction as recovered from upstream.

Expected behavior:
- UART TX high/idle -> Q1 off -> R28 pulls `Dynamixel_dir` low -> receive mode.
- UART TX low -> Q1 on -> `Dynamixel_dir` high -> transmit-low mode.

## TTL TX buffer

U7: SN74LVC1G126DBVR, SOT-23-5
- VCC -> `+3V3`
- GND -> `GND`
- A -> `UART2_TX`
- OE active-high -> `Dynamixel_dir`
- Y -> `DXL_LOCAL`
- 100nF X7R local bypass between VCC/GND

## TTL RX buffer

U6: SN74LVC1G125DBV, SOT-23-5
- VCC -> `+3V3`
- GND -> `GND`
- A -> `DXL_LOCAL`
- /OE active-low -> `Dynamixel_dir`
- Y -> `TTL_RX_OUT`
- 100nF X7R local bypass between VCC/GND

## Bus series element

R33: 150R, 0402
- pin 1 -> `DXL_LOCAL`
- pin 2 -> `DXL_DATA`

Keep receive sampling on `DXL_LOCAL`, the logic side of R33, matching upstream.

## RX combiner

U5: 74LVC1G08, SOT-23-5
- VCC -> `+3V3`
- GND -> `GND`
- input A -> `TTL_RX_OUT`
- input B -> `RS485_RX_OUT`
- output Y -> `UART2_RX`
- 100nF X7R local bypass

For a TTL-only V1 with U8 DNP, `RS485_RX_OUT` MUST be biased or strapped to logic high. It must never float. The exact upstream RS-485 receive/bias implementation remains a verification item; a DNP-safe pull-up/strap is permitted only after final schematic review.

## Optional RS-485

U8 SIT3088E remains DNP for the core XL330 build. Preserve optional footprint/layout only if board area permits.

Rules:
- DNP U8 must not load `DXL_DATA`.
- DNP U8 must not leave U5 input B floating.
- Do not allow an unpowered optional transceiver to clamp the TTL bus through protection structures.

## External DXL branches

All external branches share `DXL_DATA` but use segmented 5 V power rails.

J_DXL_A:
- GND
- `+5V_SERVO_A`
- `DXL_DATA`

J_DXL_B:
- GND
- `+5V_SERVO_B`
- `DXL_DATA`

J_DXL_C:
- GND
- `+5V_SERVO_C`
- `DXL_DATA`

J_IMU_DXL:
- GND
- selected 5 V servo branch (initially `+5V_SERVO_A`)
- `DXL_DATA`

Final physical connector pin order must be verified against ROBOTIS XL330 cable convention before footprint lock.

## Protection/test

- TP_DXL -> `DXL_DATA`
- optional TP_LOCAL -> `DXL_LOCAL`
- reserve low-capacitance ESD device from `DXL_DATA` to GND at off-board connector corridor
- do not finalize ESD part until capacitance/clamp/leakage and 1 Mbps edge behavior are reviewed

## Placement rules

1. U6/U7/R33 physically close together.
2. R33 should sit between logic cluster and external connector/data trunk.
3. ESD device should sit on connector side of R33, very close to the off-board entry/exit point.
4. Q1/R26/R27/R28 should sit adjacent to U6/U7 to keep `Dynamixel_dir` compact.
5. Keep UART/DXL logic away from high-current servo branch neck-downs and switching-current return paths.
6. Provide continuous GND reference under UART/DXL traces.

## ERC expectations

Before this sheet can enter REVIEW:
- no floating U5 input
- no unconnected U6/U7 OE
- no conflicting push-pull drivers on DXL_LOCAL
- all logic IC power pins connected and decoupled
- intentional DNP paths marked explicitly
- connector power/data nets labeled unambiguously
- power flags only where electrically appropriate

## Bench validation

After assembly:
1. power host logic only, no servos
2. verify UART2_TX idle high
3. verify `Dynamixel_dir` low while idle
4. send 0x00/0x55/0xAA patterns at 1 Mbps and scope TX, direction, DXL_LOCAL, DXL_DATA
5. verify RX buffer disabled during TX-low intervals and returns to receive
6. attach one XL330 and ping/read
7. attach imu_to_dxl and verify shared bus
8. grow to multiple servo branches and inspect ringing/turnaround

## Fabrication status

This specification is implementation-ready, but the KiCad schematic is not yet electrically instantiated and no real KiCad ERC has passed. Do not fabricate based on the skeleton alone.
