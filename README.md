# Radxa ZERO 3W Robot HAT

A custom robot HAT for **Radxa ZERO 3W**, derived from the architecture of Pollen Robotics' [`elec_RPI_Robot_HAT`](https://github.com/pollen-robotics/elec_RPI_Robot_HAT) and intended for small humanoid / MicroDuck-style robots.

## Project goals

- Direct 40-pin connection to Radxa ZERO 3W
- Dynamixel TTL bus for XL330-series actuators
- Optional RS-485 motor bus
- I2C sensor bus and Qwiic expansion
- On-board IMU
- I2S audio codec
- MEMS microphone input
- Speaker output
- Wide-range motor/system power input
- Regulated 5 V rail suitable for powering the Radxa ZERO 3W
- Compact PCB targeting the Radxa ZERO 3W footprint

## Design baseline

Reference hardware:

- Pollen Robotics `elec_RPI_Robot_HAT`
- Radxa ZERO 3W / RK3566 40-pin header
- MicroDuck hardware/software architecture

The original Pollen board integrates IMU, Dynamixel TTL/RS-485, audio, Qwiic expansion and a 5-28 V power architecture. This project adapts that concept specifically for the Radxa ZERO 3W instead of treating Raspberry Pi compatibility as the primary constraint.

## Planned architecture

```text
Battery / DC input
       |
       +---- Motor VBUS ----------------------> Dynamixel connectors
       |
       +---- DC/DC 5 V ----------------------> Radxa ZERO 3W

Radxa ZERO 3W 40-pin header
       |
       +---- UART2 --------> Dynamixel half-duplex interface
       +---- I2C3 ---------> IMU / codec control / Qwiic / sensors
       +---- I2S3 ---------> Audio codec <-> microphone / speaker
       +---- GPIO ---------> enable / direction / status functions
```

## Repository structure

```text
docs/                 Design and execution documents
hardware/kicad/       KiCad schematic and PCB files
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

**Phase 0 - Project definition / architecture**

See [`docs/00_PROJECT_PLAN.md`](docs/00_PROJECT_PLAN.md).

## Design rule

No PCB will be released for fabrication until power-path review, Radxa GPIO electrical review, ERC/DRC, connector polarity verification and a dedicated pre-fabrication checklist are completed.

## License

License selection will be finalized after checking compatibility with the upstream Pollen Robotics hardware license and any reused design files.
