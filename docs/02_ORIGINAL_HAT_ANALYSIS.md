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

For this strict port, both upstream Dynamixel TTL and RS-485 circuitry remain populated according to the upstream assembly intent. TTL is the primary expected path for the target XL330-class actuator set; changing RS-485 population is outside this port and requires a separate reviewed BOM variant.

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

For the strict Radxa port this is not required for normal operation. The upstream
U4 circuit and routed footprint are preserved, with U4 remaining DNP as released
upstream.

This also avoids unnecessary I2C-address occupancy and Raspberry Pi-specific assumptions.

## What is preserved from upstream

- Single-PCB power tree and protection circuit
- Dynamixel physical connectors and half-duplex implementation
- TTL and RS-485 channels
- BMI088 IMU block
- I2S codec / microphone / speaker implementation
- All four Qwiic expansion connectors (J5 hardware I2C plus J6/J7/J8 software-I2C GPIO pairs)
- Hierarchical KiCad project organization and routed PCB

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

The project imports the complete upstream source and applies a controlled,
host-facing adaptation:

```text
Upstream single-board source
     |
     +--> preserve schematic, connector topology and routed PCB
     +--> map physical 40-pin functions to RK3566 names
     +--> DNP only unsupported Raspberry Pi-specific options
     +--> verify mechanics, power behavior and device tree
```

## Licensing note

The upstream repository is Apache-2.0 licensed. The active derivative records the
source repository and exact imported commit, preserves upstream authorship, and
documents modifications in `09_STRICT_PORT_CHANGE_MATRIX.md`.
