# 02 - Upstream Pollen Robot HAT Analysis

## Reference

Upstream project:

- https://github.com/pollen-robotics/elec_RPI_Robot_HAT

The upstream board is a KiCad 9 Raspberry Pi-format robot HAT designed by Pollen Robotics / Hugging Face for small and medium robots.

## Main functional blocks

Based on the upstream repository, the board combines:

1. **40-pin host interface**
2. **Dynamixel communication**
   - TTL
   - RS-485
3. **IMU / sensors** over I2C
4. **Audio subsystem**
   - I2S codec
   - integrated MEMS microphone
   - speaker / external microphone connectivity
5. **Qwiic-style 3.3 V expansion**
6. **Wide-range power subsystem**
   - upstream target input range: 5-28 V
   - motor connector can act as power input

## Relevant upstream files

- `main.kicad_sch` - top-level schematic / 40-pin interface
- `power.kicad_sch` - power subsystem
- `dynamixel.kicad_sch` - TTL and RS-485 motor communication
- `sensors.kicad_sch` - IMU/sensor subsystem
- audio-related hierarchical circuitry in the project
- `docs/config.txt` - Raspberry Pi interface enablement reference

## Identified IC/functions

### Dynamixel

The upstream Dynamixel schematic includes an **SP3485-class RS-485 transceiver** for differential communication as well as TTL-oriented motor communication circuitry.

For this project, Dynamixel TTL is the primary path because the target MicroDuck-style actuator set is XL330-class TTL. RS-485 will be retained only if routing/space/cost permit, or made DNP-capable.

### Sensors

The upstream sensor section uses a 6-axis IMU architecture and documents I2C-connected accelerometer/gyroscope functions.

The Radxa redesign should preserve a locally mounted IMU but must verify:

- exact current-production part
- I2C addresses
- pull-up values
- interrupt usage
- placement sensitivity

### Audio

The upstream HAT provides both input and output audio and an integrated MEMS microphone. The Radxa redesign will retain an I2S codec-based architecture because ZERO 3W exposes an appropriate I2S interface on its 40-pin header.

### HAT EEPROM

The upstream main schematic includes HAT identification at I2C address `0x50` for Raspberry Pi HAT identification.

For a Radxa-specific board this is not required for normal operation. V1 policy:

- omit it, or
- leave footprint DNP if upstream compatibility becomes useful later.

This also avoids unnecessary I2C-address occupancy and Raspberry Pi-specific assumptions.

## What can be reused conceptually

- Power-tree topology and protection ideas
- Dynamixel physical connector architecture
- Half-duplex UART concept
- RS-485 optional channel
- IMU block
- I2S codec / microphone / speaker architecture
- Qwiic expansion philosophy
- Hierarchical KiCad project organization

## What must NOT be copied blindly

### Host pin names

Raspberry Pi BCM GPIO names cannot be used as Radxa signal definitions. Connections must be based on **physical header pin + RK3566 mux function**.

### Device-tree assumptions

Raspberry Pi `config.txt` configuration does not apply to Radxa Linux. Radxa pinmux/device-tree overlays must be maintained separately.

### HAT identification

Raspberry Pi HAT EEPROM behavior is not a functional requirement.

### Power behavior

The upstream board's supply architecture needs a fresh review for:

- Radxa ZERO 3W peak 5 V demand
- backfeed behavior
- regulator thermal margin
- MicroDuck actuator load
- selected battery voltage

### Mechanical assumptions

Even though the boards share the 40-pin ecosystem, all hole locations and connector clearances will be independently verified from Radxa mechanical documentation.

## Upstream-to-Radxa adaptation strategy

Rather than redraw everything from scratch without reference, the project will use a controlled block-by-block adaptation:

```text
Upstream block
     |
     +--> understand schematic intent
     +--> identify Raspberry-Pi-specific assumptions
     +--> map required interface to RK3566
     +--> update component/rating choices
     +--> recreate as Radxa-specific KiCad sheet
     +--> review independently
```

## Licensing note

Before directly copying schematic/PCB source content into this repository, the upstream hardware license and attribution requirements must be checked. Until that review is completed, this repository will clearly document upstream references and independently create the Radxa-specific implementation.
