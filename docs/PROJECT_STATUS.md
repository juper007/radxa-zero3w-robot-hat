# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 0 - Architecture and requirements**

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

## In progress

- [ ] Power subsystem detailed design
- [ ] Radxa power budget
- [ ] Dynamixel bus current budget
- [ ] Component selection

## Next actions

1. Reconstruct and analyze the upstream power sheet component-by-component.
2. Define maximum motor VBUS current and connector requirements.
3. Select the 5 V DC/DC architecture for the Radxa ZERO 3W.
4. Design input protection and backfeed prevention.
5. Produce `docs/05_POWER_DESIGN.md`.
6. Begin `hardware/kicad/power.kicad_sch`.
7. Review before moving to Dynamixel circuitry.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use Radxa ZERO 3W as the primary host | Target MicroDuck DIY compute module |
| 2026-09-09 | Direct 40-pin HAT connection | Avoid unnecessary adapter PCB |
| 2026-09-09 | Dynamixel TTL is mandatory | XL330-class target actuators use TTL bus |
| 2026-09-09 | RS-485 is optional/DNP-capable | Not required for core MicroDuck actuator set |
| 2026-09-09 | Retain audio in V1 scope | Microphone and speaker are desired robot functions |
| 2026-09-09 | Prefer 4-layer PCB | Better ground integrity, power distribution and noise control |
| 2026-09-09 | Do not fabricate until explicit design review | Power and connector mistakes can damage Radxa/servos |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.1-dev` - documentation/architecture only. **Not fabrication-ready.**
