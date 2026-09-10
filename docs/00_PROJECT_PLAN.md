# 00 - Project Plan

## Objective

Design, validate and manufacture a compact **Radxa ZERO 3W Robot HAT** inspired by Pollen Robotics' `elec_RPI_Robot_HAT`, with a focus on MicroDuck-style robots using Dynamixel XL330 actuators.

## Scope

### V1 required

- Radxa ZERO 3W 40-pin connection
- 3.3 V logic compatibility
- UART-based Dynamixel TTL interface
- I2C sensor/control bus
- I2S audio interface
- On-board IMU
- Audio codec
- MEMS microphone support
- Speaker output
- 5-28 V system/motor input target
- 5 V regulated Radxa supply
- Reverse-polarity / transient / over-current design review
- Test points for major rails and buses

### V1 optional / DNP-capable

- RS-485 Dynamixel interface
- HAT identification EEPROM
- Secondary microphone connector
- Extra Qwiic ports

## Execution phases

### Phase 0 - Architecture and requirements

Deliverables:

- Project requirements
- Upstream HAT functional analysis
- Radxa pin mapping
- Block architecture
- Power budget assumptions

Exit criteria:

- Every Radxa-connected net has a documented physical pin and RK3566 function.
- Required peripherals are assigned without known mux conflicts.

### Phase 1 - Power subsystem

Deliverables:

- Input protection design
- Motor VBUS path
- 5 V DC/DC supply
- 3.3 V usage definition
- Power sequencing/backfeed analysis
- Power-tree schematic

Exit criteria:

- Input voltage range and component voltage ratings are consistent.
- Worst-case current and thermal margins are documented.
- No unintended 5 V or 3.3 V backfeed path remains.

### Phase 2 - Dynamixel interface

Deliverables:

- UART2 interface
- Half-duplex direction logic
- TTL bus protection
- Dynamixel connectors
- Optional RS-485 channel

Exit criteria:

- 1 Mbps bus target supported with appropriate logic thresholds and timing.
- Connector power polarity and signal order independently reviewed.

### Phase 3 - Sensors and I2C

Deliverables:

- IMU interface
- I2C pull-up strategy
- Qwiic expansion
- Optional external ToF/sensor connectors

Exit criteria:

- Address conflicts checked.
- Bus pull-up equivalent resistance reviewed.

### Phase 4 - Audio

Deliverables:

- I2S3 interface
- Codec schematic
- MEMS microphone input
- Speaker output stage / connector

Exit criteria:

- Radxa I2S pin mux confirmed.
- Analog and switching-current layout constraints documented.

### Phase 5 - KiCad schematic integration

Deliverables:

- Hierarchical KiCad schematic
- Footprint assignment
- ERC cleanup
- BOM draft

Exit criteria:

- Zero unexplained ERC errors.
- All critical components have verified manufacturer part numbers.

### Phase 6 - PCB layout

Target:

- Radxa ZERO 3W footprint class, approximately 65 x 30 mm where practical
- 4-layer PCB preferred

Suggested stack:

1. Top - components/signals
2. Inner 1 - solid GND
3. Inner 2 - power / low-speed signals as needed
4. Bottom - components/signals

Deliverables:

- Board outline
- Placement
- Routing
- Ground strategy
- Thermal strategy
- DRC report

### Phase 7 - Pre-fabrication review

Mandatory review:

- Power polarity
- Connector orientation
- 40-pin header orientation
- Radxa pin mapping
- Dynamixel pin order
- Regulator feedback network
- component package/pin numbering
- voltage ratings
- copper width/current capacity
- mounting-hole locations
- courtyard/mechanical collisions
- ERC and DRC

### Phase 8 - Manufacturing package

Deliverables:

- Gerbers
- drill files
- BOM
- pick-and-place
- assembly drawing
- fabrication notes

### Phase 9 - Bring-up

Bring-up order:

1. Visual/continuity inspection with Radxa disconnected
2. Validate input protection
3. Validate 5 V rail under dummy load
4. Verify no backfeed to host
5. Connect Radxa without motors
6. Validate I2C
7. Validate IMU
8. Validate UART/Dynamixel with one actuator
9. Validate multi-actuator bus
10. Validate I2S/audio
11. Full robot load test

## Version strategy

- `v0.x`: development, not fabrication-approved
- `v1.0-rcN`: fabrication candidate
- `v1.0`: electrically and mechanically validated revision

## Source of truth

All project documentation, KiCad source files, manufacturing artifacts and test notes will be maintained in this repository.
