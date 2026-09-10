# Radxa ZERO 3W Robot HAT

A custom robot HAT for **Radxa ZERO 3W**, derived in part from Pollen Robotics' Apache-2.0 [`elec_RPI_Robot_HAT`](https://github.com/pollen-robotics/elec_RPI_Robot_HAT) and intended for MicroDuck-style robots.

## V1 goals

- Direct 40-pin connection to Radxa ZERO 3W
- DYNAMIXEL TTL bus for 15 × XL330-series actuators
- Connector for current MicroDuck `imu_to_dxl` node on the same TTL bus
- Optional/DNP RS-485 compatibility path
- I2C/Qwiic sensor expansion
- Optional auxiliary on-board IMU compatibility footprint/design
- I2S audio codec
- MEMS microphone input
- Speaker output
- External **regulated 5 V high-current** robot supply
- Independently protected/backfeed-blocked 5 V Radxa branch
- Compact PCB targeting the Radxa ZERO 3W footprint

## Frozen V1 power architecture

```text
External regulated 5 V high-current supply
                 |
               XT60
                 |
             20 A fuse
                 |
       LM74700-Q1 + N-FET
                 |
              +5V_SYS
        __________|____________________
       |           |          |        |
       v           v          v        v
 SERVO_A      SERVO_B     SERVO_C   TPS259470A
 5 motors      5 motors    5 motors      |
                                      +5V_RADXA
                                         |
                                  Radxa pins 2/4
```

There is **no 12–28 V to 5 V high-power buck converter in V1**. The 5 V source must already be regulated and sized for the robot load.

## Main host interfaces

```text
Radxa ZERO 3W 40-pin header
       |
       +---- UART2 pins 8/10 --> hardware half-duplex logic --> DXL_DATA
       |                              |--> 15 XL330
       |                              `--> imu_to_dxl ID 200
       +---- I2C3 pins 3/5 ----> codec control / Qwiic / optional sensors
       +---- I2S3 -------------> audio codec <-> microphone / speaker
       +---- +3V3 -------------> HAT logic supply
```

Current MicroDuck software uses `/dev/ttyS2` at 1 Mbps and reads the `imu_to_dxl` board together with all 15 servos. The legacy HAT BMI088 is therefore not a mandatory sensor for the current control loop.

## Repository structure

```text
docs/                 Design and execution documents
hardware/kicad/       KiCad schematic and PCB files + connectivity checks
hardware/libraries/   Project symbols and footprints
hardware/mechanical/  Board outline and mechanical references
production/gerber/    Manufacturing Gerbers
production/bom/       BOM exports
production/assembly/  Assembly documentation
software/overlays/    Radxa device-tree overlays
software/setup/       OS/interface setup scripts
software/test/        Hardware bring-up test utilities
reference/            Reference notes and source links
```

## Current status

Active development. See [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the exact phase and fabrication blockers.

## Design rule

No PCB is fabrication-approved until power-path review, exact footprint/pad verification, Radxa GPIO electrical review, schematic ERC, PCB DRC, connector polarity/orientation review, high-current layout review and the dedicated pre-fabrication checklist are complete.

## Upstream attribution

Portions of the architecture and planned DYNAMIXEL/audio implementation are derived from or informed by Pollen Robotics' `elec_RPI_Robot_HAT`, distributed under Apache License 2.0. Modified derivative files will carry an explicit modification notice and preserve applicable attribution.
