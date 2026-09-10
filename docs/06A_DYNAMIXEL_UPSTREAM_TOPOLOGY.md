# Dynamixel Upstream Topology Recovery

Status: DESIGNING / evidence-backed recovery  
Date: 2026-09-09

## Goal

Recover the proven half-duplex DYNAMIXEL interface from Pollen Robotics' `elec_RPI_Robot_HAT` before translating it to the Radxa-specific V1 sheet. This avoids inventing a direction-control scheme that may not match the software stack.

## Verified upstream facts

The upstream KiCad 9 `dynamixel.kicad_sch` contains the following TTL logic devices:

- U5: `74LVC1G08`, SOT-23-5
- U6: `SN74LVC1G125DBV`, SOT-23-5
- U7: `SN74LVC1G126DBVR`, SOT-23-5
- U8: `SIT3088E`, MSOP-8-EP, used for the optional RS-485 path

The production BOM additionally identifies:

- U5 LCSC C7666
- U6 LCSC C3040625
- U7 LCSC C7834
- U8 LCSC C2922535
- R8 = 100 ohm
- R33 = 150 ohm
- TH1 = 100 ohm thermistor
- J13/J14 = JST EH 3-pin DYNAMIXEL connectors
- J3/J11 = JST EH 4-pin DYNAMIXEL connectors

The upstream schematic defines bus alias `Dyn_UART` containing `DynUART_RTS`, `DynUART_Tx`, and `DynUART_Rx`. It also contains local labels `IO_14`, `IO_15`, and `Dynamixel_dir`.

`IO_14`/`IO_15` correspond to the Raspberry-Pi-style UART TX/RX allocation. On Radxa ZERO 3W those same physical header locations are pin 8 UART2_TX_M0 and pin 10 UART2_RX_M0, which is exactly the UART used by current MicroDuck software (`/dev/ttyS2`).

## Direction-control finding

The upstream design uses U5/U6/U7 rather than exposing an additional required HAT direction GPIO to the host. The direction node is named `Dynamixel_dir` and is associated with the UART/TX logic in the upstream sheet. This is important because current MicroDuck user-space code opens `/dev/ttyS2` as an ordinary serial port and does not expose a separate GPIO-direction operation in the normal bus API.

Therefore V1 will preserve the upstream auto/dedicated hardware direction topology rather than replacing it with a new software-controlled DIR GPIO.

## Current V1 mapping

```text
Radxa pin 8 / UART2_TX_M0 -> TX/direction logic -> TTL bus driver -> DXL_DATA
DXL_DATA -> receive buffer -> Radxa pin 10 / UART2_RX_M0

+3V3 (from Radxa) -> U5/U6/U7 logic VCC
GND -> common logic/servo reference
+5V_SERVO_A/B/C -> servo connector power
```

The same `DXL_DATA` logical signal is shared across all three 5-servo power groups. Power segmentation does not imply three UART buses.

## Latest MicroDuck IMU implication

Current MicroDuck software performs a combined DYNAMIXEL `sync_read` covering the 15 servos plus `imu_to_dxl` ID 200. The IMU therefore rides this same physical bus. For this PCB project, the old HAT BMI088 is now treated as optional/compatibility hardware rather than a requirement for the current control loop.

## RS-485 policy

RS-485 remains optional/DNP in V1. The upstream U8 SIT3088E path is useful as a reference but must not add loading or routing complexity to the primary XL330 TTL path when not populated.

## Implementation constraints

- Logic side is 3.3 V.
- Radxa UART pins must never receive an unsafe 5 V level.
- Preserve tri-state behavior during TX/RX turnaround.
- Keep a source-series tuning resistor footprint on DXL_DATA/TX drive path.
- Add low-capacitance ESD protection footprint at the off-board DATA network.
- Add a DXL_DATA test point.
- Keep connector GND return direct and low impedance.
- Do not add a mandatory host DIR GPIO unless later evidence proves the upstream/current software requires one.

## Evidence confidence

HIGH:
- device identities and production part numbers
- presence of IO_14, IO_15 and Dynamixel_dir labels
- Radxa UART2 pins 8/10 and current `/dev/ttyS2` usage
- current software's combined servo + imu_to_dxl bus

MEDIUM / still being translated:
- exact passive placement around U5/U6/U7
- exact Boolean relationship used to create `Dynamixel_dir`
- which of the upstream 100/150-ohm parts is in the TTL versus RS-485 segment

Those MEDIUM items must be recovered from the source schematic before the V1 sheet is marked REVIEW.

## Licensing

The upstream hardware repository is Apache-2.0. Any directly adapted schematic sections will retain upstream attribution and a prominent modification notice. The upstream repository did not expose a separate `NOTICE` file at the checked path.
