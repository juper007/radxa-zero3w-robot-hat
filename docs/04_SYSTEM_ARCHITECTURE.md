# 04 - System Architecture

## Top-level architecture

```text
                 +----------------------+
                 |   Radxa ZERO 3W       |
                 |       RK3566          |
                 +----------+-----------+
                            |
                       40-pin header
                            |
       +--------------------+--------------------+
       |                    |                    |
     UART2                 I2C3                I2S3
       |                    |                    |
       v                    v                    v
+--------------+     +-------------+      +-------------+
| Dynamixel    |     | Sensors /   |      | Audio codec |
| half-duplex  |     | expansion   |      | + mic/spkr  |
+------+-------+     +------+------+      +------+------+ 
       |                    |                    |
       v                    v                    v
 XL330 TTL bus          IMU / Qwiic        Mic / Speaker


Robot battery / DC input
          |
          +-----------------------> Motor VBUS
          |
          +--> protection --> DC/DC 5 V --> Radxa ZERO 3W
```

## Design partitions

### A. Host interface

Responsibilities:

- 2x20 2.54 mm 40-pin connector
- host 5 V connection
- host 3.3 V logic reference
- I2C3
- UART2
- I2S3
- reserved GPIO

Design rule: every host signal must be referenced by physical header pin and RK3566 function.

### B. Power subsystem

Responsibilities:

- robot/battery input
- reverse-polarity strategy
- transient protection
- bulk capacitance
- motor VBUS distribution
- 5 V DC/DC conversion
- host-power isolation/backfeed review
- status/test points

The detailed design must distinguish two current domains:

1. high-current / noisy motor domain
2. host, sensor and audio domain

They share ground electrically, but placement and current-return paths must minimize noise coupling.

### C. Dynamixel subsystem

Primary target: 3-wire Dynamixel TTL bus for XL330-class actuators.

Logical path:

```text
UART2_TX ----+
             +--> direction / half-duplex logic --> DXL_DATA
UART2_RX <---+

Motor VBUS --------------------------------------> DXL_V+
GND ---------------------------------------------> DXL_GND
```

Requirements:

- reliable 1 Mbps operation
- correct half-duplex turnaround
- protection that does not excessively load/distort the bus
- multiple physical connectors may share the same logical bus
- clear polarity/orientation markings

Optional RS-485 transceiver is a secondary block and may be DNP in V1.

### D. Sensor subsystem

Main I2C3 bus supports:

- on-board IMU
- codec control
- Qwiic expansion
- optional external sensors / ToF

Sensor layout principles:

- place IMU away from switching inductors
- avoid placement directly adjacent to high-current motor connectors
- provide clean local decoupling
- consider mechanical vibration and board flex

### E. Audio subsystem

Host interface: I2S3 plus I2C control.

Planned functions:

- codec
- microphone input
- speaker output
- optional external mic/speaker connectors

Audio design must explicitly document:

- master/slave clock roles
- sample-rate assumptions
- MCLK requirement
- analog supply filtering
- microphone bias where applicable
- output load / amplifier requirement

## Proposed KiCad hierarchy

```text
radxa_zero3w_robot_hat.kicad_sch
  |
  +-- host_interface.kicad_sch
  +-- power.kicad_sch
  +-- dynamixel.kicad_sch
  +-- sensors.kicad_sch
  +-- audio.kicad_sch
```

This mirrors the useful functional separation of the upstream Pollen design while making host assumptions explicitly Radxa-specific.

## PCB floor-plan concept

```text
+----------------------------------------------------------------+
| Motor/DC input     Power stage                     DXL ports     |
| [connector]       [TVS/FET/DC-DC]                  [TTL/485]     |
|                                                                |
|             GND / keep noisy switching compact                 |
|                                                                |
| IMU + Qwiic                40-pin host             Audio        |
| [quiet area]               connector               codec/mic    |
+----------------------------------------------------------------+
```

The final physical orientation depends on how the HAT stacks in the robot. Connector accessibility takes precedence over cosmetic symmetry.

## Four-layer strategy

Preferred initial stack:

- L1: components + signals + high-current local pours
- L2: uninterrupted GND plane
- L3: power distribution + limited low-speed signals
- L4: signals + components as required

Keep return paths continuous beneath UART, I2C and I2S signals. Avoid splitting the reference plane under digital buses.

## Key architecture risks

1. **5 V host power current/thermal margin**
2. **USB and HAT 5 V backfeed interaction**
3. **Dynamixel motor transients coupling into Radxa**
4. **UART2 console conflict in Linux**
5. **I2S clocking/pinmux configuration**
6. **I2C pull-up accumulation with external Qwiic boards**
7. **IMU noise/vibration from placement**
8. **Mechanical connector interference in the robot enclosure**

Each risk must be closed or explicitly accepted before the first fabrication release.
