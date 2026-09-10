# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 - Power subsystem detailed design**

## Completed

- [x] Repository initialized
- [x] Project goals documented
- [x] Initial functional/electrical/mechanical requirements
- [x] Upstream Pollen Robot HAT architecture analysis
- [x] Initial Radxa ZERO 3W 40-pin mapping
- [x] Top-level system architecture
- [x] KiCad hierarchy proposal
- [x] Preliminary PCB layer/floor-plan strategy
- [x] Initial architecture-risk list
- [x] V1 power-domain architecture
- [x] Input protection strategy
- [x] Motor VBUS / host 5 V separation strategy
- [x] USB-C / HAT backfeed identified as mandatory validation item
- [x] Power-sheet KiCad implementation contract
- [x] Provisional power BOM created
- [x] Initial power bring-up sequence defined

## In progress

- [ ] Freeze normal robot supply voltage and maximum VIN
- [ ] Calculate 15-servo XL330 worst-case/current-budget scenarios
- [ ] Select exact 5 V synchronous buck regulator
- [ ] Select exact reverse-polarity / ideal-diode implementation
- [ ] Select TVS and fuse ratings
- [ ] Select final power connector
- [ ] Create `hardware/kicad/power.kicad_sch`

## Next actions

1. Build the XL330 bus current budget for 15 servos.
2. Freeze the prototype input-voltage target around the intended MicroDuck actuator supply.
3. Compare suitable high-input-voltage 5 V / >=5 A synchronous buck regulators.
4. Select protection MOSFET/controller, TVS and fuse.
5. Freeze power-section footprints.
6. Implement `hardware/kicad/power.kicad_sch` in KiCad 9 format.
7. Run ERC and perform a power schematic design review.
8. Only then move to the Dynamixel TTL interface sheet.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use Radxa ZERO 3W as the primary host | Target MicroDuck DIY compute module |
| 2026-09-09 | Direct 40-pin HAT connection | Avoid unnecessary adapter PCB |
| 2026-09-09 | Dynamixel TTL is mandatory | XL330-class target actuators use TTL bus |
| 2026-09-09 | RS-485 is optional/DNP-capable | Not required for core MicroDuck actuator set |
| 2026-09-09 | Retain audio in V1 scope | Microphone and speaker are desired robot functions |
| 2026-09-09 | Prefer 4-layer PCB | Better ground integrity, power distribution and noise control |
| 2026-09-09 | Separate MOTOR_VBUS and +5V_RADXA | Prevent motor rail from reaching host directly and improve noise control |
| 2026-09-09 | Target a practical 5 A class host regulator | Provide margin for Radxa and attached low-voltage peripherals; final thermal validation required |
| 2026-09-09 | Keep configurable reverse-current protection in first prototype | USB-C and HAT 5 V coexistence must be proven before simplifying |
| 2026-09-09 | Do not fabricate until explicit design review | Power and connector mistakes can damage Radxa/servos |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.2-dev` - power architecture and implementation specification established. **Not fabrication-ready.**
