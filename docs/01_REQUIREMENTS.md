# 01 - Design Requirements

## Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Mount/connect directly to Radxa ZERO 3W 40-pin header | Must |
| FR-002 | Provide Dynamixel TTL communication for XL330-class servos | Must |
| FR-003 | Support target UART bus rate of at least 1 Mbps | Must |
| FR-004 | Provide I2C sensor/control bus | Must |
| FR-005 | Provide on-board 6-axis IMU | Must |
| FR-006 | Provide I2S audio connectivity | Must |
| FR-007 | Provide microphone input | Must |
| FR-008 | Provide speaker output | Must |
| FR-009 | Accept wide-range robot supply, target 5-28 V | Must |
| FR-010 | Generate regulated 5 V suitable for Radxa ZERO 3W | Must |
| FR-011 | Provide motor/system power distribution | Must |
| FR-012 | Provide accessible test points for critical rails/buses | Must |
| FR-013 | Provide optional RS-485 motor interface | Should |
| FR-014 | Provide 3.3 V Qwiic-style expansion | Should |

## Electrical requirements

- Radxa-facing GPIO signals shall use 3.3 V-compatible logic levels.
- No external circuit shall force >3.3 V onto an RK3566 GPIO.
- 5 V rail must be reviewed for host backfeed behavior before fabrication.
- Motor current paths shall not share narrow signal return paths.
- DC/DC input and switching nodes shall be kept away from audio analog inputs and IMU-sensitive areas.
- All components exposed directly to the robot input supply must have suitable voltage derating above the maximum intended operating voltage.
- Bulk and local decoupling must be provided close to motor-power and regulator interfaces.
- Dynamixel connector polarity shall be treated as a critical safety item.

## Interface allocation baseline

Planned host interfaces:

- I2C3 M0: physical pins 3 / 5
- UART2 M0: physical pins 8 / 10
- I2S3: physical pins 12 / 35 / 38 / 40
- 5 V: physical pins 2 / 4
- 3.3 V: physical pins 1 / 17
- GND: multiple ground pins

These assignments must be rechecked against the selected Radxa OS/device-tree configuration immediately before schematic release.

## Mechanical requirements

- Target PCB footprint: approximately Radxa ZERO 3W size class (65 x 30 mm) where connector and power-stage placement permits.
- Maintain access/clearance for the Radxa microSD, USB, HDMI and antenna regions as required by the final stack orientation.
- Pin 1 and connector orientation shall be unambiguous on both copper documentation and silkscreen.
- Mounting holes shall align to verified Radxa ZERO 3W mechanical drawings before fabrication.

## PCB requirements

- KiCad 9 project format.
- 4-layer PCB preferred.
- Continuous inner ground plane preferred.
- Keep switching regulator hot loop compact.
- Keep IMU away from inductors, high-current motor connectors and board flex concentration where practical.
- Keep audio analog routing away from switching nodes and Dynamixel power traces.
- Use wide copper/pours for motor and input-power paths based on calculated current requirements.

## Verification requirements

Before Gerber release:

- ERC completed with no unexplained errors.
- DRC completed with no unexplained errors.
- Independent pin-by-pin 40-pin header verification.
- Connector pin-1/polarity verification.
- Power-tree current and thermal calculation.
- Datasheet pin-number cross-check for every IC.
- Footprint/package cross-check for every IC and connector.
- Mechanical collision review.

## Open parameters

The following values will be finalized during detailed design:

- Maximum continuous motor-bus current
- Exact 5 V regulator output-current target
- Input connector family
- Number of Dynamixel connectors
- Whether RS-485 is populated in V1
- Audio speaker power target
- Exact microphone implementation
