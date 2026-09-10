# Dynamixel TTL Subsystem — V1

Status: DESIGNING  
Target: Radxa ZERO 3W UART2 + 15 x XL330-M288-T

## 1. Scope

V1 requires the 3-wire DYNAMIXEL TTL bus used by XL330-M288-T. RS-485 is optional/DNP and must not complicate the primary TTL path.

## 2. Host interface

Radxa ZERO 3W physical header:
- pin 8: UART2_TX_M0
- pin 10: UART2_RX_M0
- logic level: 3.3 V

Software requirement: UART2 is also used by the default debug console on some Radxa configurations. Boot console/getty must be disabled before the robot bus is used. MicroDuck software targets `/dev/ttyS2` at 1 Mbps.

## 3. Half-duplex topology

XL330 uses one bidirectional DATA wire. The host UART therefore needs TX/RX direction handling.

V1 topology follows the proven Pollen Robot HAT concept:

```text
Radxa UART2_TX ---- direction/logic gating ----+---- DXL_DATA
                                               |
Radxa UART2_RX <-------------------------------+

+5V_SERVO_x ---------------------------------------- DXL VCC
GND ----------------------------------------------- DXL GND
```

The actual transceiver/gate implementation will be derived from the upstream Pollen `dynamixel.kicad_sch`, retaining 3.3 V-safe logic and the proven timing behavior at 1 Mbps.

## 4. Connector strategy

The power sheet distributes three 5-servo power groups A/B/C. The TTL DATA signal remains one logical bus unless signal-integrity testing proves segmentation is needed.

Each servo connector exposes:
- GND
- +5V_SERVO branch
- DXL_DATA

Connector pin order must match the selected XL330 cable/connector convention and will be independently checked before footprint lock.

## 5. Electrical rules

- Do not expose Radxa GPIO directly to 5 V.
- All UART-side logic is 3.3 V compatible.
- Keep DXL_DATA away from high di/dt power loops where practical.
- Add a modest source-series resistor footprint close to the driver for edge-rate/ringing tuning; initial population TBD after reviewing upstream values.
- Provide test point on DXL_DATA.
- Avoid unnecessary pull-ups that fight the active half-duplex driver.
- Ground reference must be continuous between Radxa and servos.

## 6. Protection

Because connectors leave the PCB, reserve optional ESD protection on DXL_DATA. Select a low-capacitance device compatible with a 1 Mbps UART and 3.3 V signaling.

Power transient protection remains in the power subsystem and must not be duplicated with large capacitance on DATA.

## 7. Bring-up

1. Radxa powered, servo power disabled.
2. Confirm UART2 console/getty disabled.
3. Loopback/test UART2 TX/RX at 1 Mbps.
4. Populate half-duplex interface.
5. Scope TX direction and DXL_DATA with no servo.
6. Connect one XL330 with current-limited 5 V servo supply.
7. Ping/read model/position.
8. Add servos incrementally.
9. Validate 15-servo bus traffic during motion.
10. Inspect ringing, ground bounce and UART errors.

## 8. Acceptance criteria

- Reliable 1 Mbps communication with one XL330.
- Reliable enumeration/traffic with all 15 servos.
- No 5 V stress at Radxa UART pins.
- No bus contention during TX-to-RX turnaround.
- No unexplained framing/CRC errors under aggressive motion.
- Connector pinout independently verified.

## 9. Next implementation work

- Import/recreate the upstream proven TTL gate/transceiver section.
- Freeze exact logic device and passive values.
- Create project-local symbol/footprint mapping where necessary.
- Create `hardware/kicad/dynamixel.kicad_sch`.
- Add automated pin/net invariants similar to the power checker.
