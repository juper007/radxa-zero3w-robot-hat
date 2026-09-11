# 00 — Strict-port project plan

## Objective

Port Pollen Robotics' `elec_RPI_Robot_HAT` to the Radxa ZERO 3W while preserving the upstream single-board HAT architecture.

## Architectural invariants

The strict port shall preserve unless a demonstrated Radxa incompatibility requires otherwise:

1. one PCB, approximately 65 × 31 mm;
2. four copper layers and the upstream routed-layout baseline;
3. the 5–28 V input and on-board conversion concept;
4. on-board Dynamixel, sensor, audio and expansion functional blocks;
5. connector topology and assembly model.

A daughterboard, larger PCB, high-current power redesign or connector-family replacement requires a separate variant and explicit approval.

## Allowed changes

- physical 40-pin header function names and Radxa pinmux documentation;
- host-specific device-tree configuration;
- removal or DNP treatment of Raspberry Pi-only functions;
- changes required by verified Radxa electrical or mechanical incompatibility;
- silkscreen/project identity and attribution notices.

## Work phases

### 1. Establish upstream baseline

- Record the exact upstream commit.
- Import the complete KiCad schematic hierarchy, project and routed PCB.
- Capture native ERC, DRC, component, net, board-size and routing metrics.

### 2. Host-interface adaptation

- Map every used upstream header pin by physical pin number.
- Rename critical nets to RK3566 peripheral functions.
- Preserve routing where physical pins are identical.
- Mark unsupported Raspberry Pi-only options DNP rather than redesigning the board.

### 3. Mechanical verification

- Overlay the Radxa ZERO 3W mechanical drawing.
- Verify mounting holes, 40-pin orientation and connector mating height.
- Review microSD, USB-C, HDMI, camera, antenna and component keepouts.

### 4. Electrical verification

- Verify all Radxa-facing signals are 3.3 V compatible.
- Confirm I2C3 M0, UART2 M0 and I2S3 M0 device-tree ownership.
- Review 5 V HAT power and simultaneous USB-C power/backfeed behavior.
- Resolve or explicitly disposition every inherited ERC/DRC finding.

### 5. Release

- Independent schematic and PCB review.
- Generate a Radxa-specific BOM, position file and assembly drawing.
- Run staged bench bring-up before connecting motors.
- Generate Gerbers only after all release blockers are closed.

## Source of truth

The active design files are `hardware/kicad/radxa_zero3w_robot_hat.kicad_{pro,sch,pcb}` and their six upstream-derived child sheets. The change matrix in `docs/09_STRICT_PORT_CHANGE_MATRIX.md` governs scope.
