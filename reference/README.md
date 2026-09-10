# References

This directory tracks the external projects and documentation used during the Radxa ZERO 3W Robot HAT design.

## Primary upstream hardware

### Pollen Robotics elec_RPI_Robot_HAT

https://github.com/pollen-robotics/elec_RPI_Robot_HAT

Purpose:

- functional architecture reference
- Dynamixel interface reference
- power subsystem reference
- sensor / IMU reference
- audio architecture reference
- KiCad project organization reference

Important: upstream files are reference material. Direct reuse must follow the upstream license and attribution terms.

## Target robot/software

### Pollen Robotics MicroDuck

https://github.com/pollen-robotics/microduck

Useful reference areas:

- Radxa ZERO 3W configuration
- device-tree overlays
- robot bring-up
- audio/I2C configuration

Example I2C3 HAT overlay:

https://github.com/pollen-robotics/microduck/blob/main/deploy/audio/i2c3-pihat.dts

## Target SBC

### Radxa ZERO 3W documentation

https://docs.radxa.com/en/zero/zero3

Hardware interface documentation:

https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface

## Reference policy

For every critical electrical decision, prefer this order:

1. IC manufacturer datasheet
2. Radxa official schematic/hardware documentation
3. Upstream Pollen hardware source
4. Known validated open-source implementations
5. Assumptions, clearly marked for validation

Critical values copied from a reference must be independently checked before PCB fabrication.
