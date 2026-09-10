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
- [x] XL330-M288-T 15-servo current budget
- [x] V1 input architecture changed to regulated 5 V high-current supply
- [x] Removed unnecessary high-power 12–28 V to 5 V conversion from V1 scope
- [x] Separated +5V_SERVO and +5V_RADXA physical current paths
- [x] USB-C / HAT backfeed identified as mandatory validation item
- [x] TPS25947 selected as host-branch eFuse/reverse-current candidate
- [x] Main connector candidates narrowed to XT30 / XT60
- [x] 5 V TVS candidate documented with clamp-voltage limitation
- [x] Provisional power BOM revised
- [x] Initial power bring-up sequence defined

## Key electrical numbers

- XL330-M288-T recommended supply: 5.0 V
- XL330-M288-T stall current at 5 V: ~1.47 A
- 15-servo theoretical simultaneous stall: ~22.05 A
- Provisional Radxa/audio/logic design allocation: up to ~4 A
- Pathological total worst-case envelope: ~26 A
- Recommended development supply: regulated 5 V, 15–20 A class

## In progress

- [ ] Select exact main reverse-polarity MOSFET / ideal-diode controller
- [ ] Calculate PCB copper loss and temperature rise at 10 A / 15 A / 20 A
- [ ] Freeze XT30 versus XT60 based on mechanical/current review
- [ ] Select exact TPS25947 suffix and host-current-limit network
- [ ] Decide servo branch grouping and connector count
- [ ] Implement `hardware/kicad/power.kicad_sch`

## Next actions

1. Perform high-current copper/connector loss calculations.
2. Select main protection MOSFET/controller.
3. Freeze main connector.
4. Freeze TPS25947 variant and calculate ILIM/dVdt components.
5. Finalize servo branch topology.
6. Implement KiCad power schematic.
7. Run ERC and power design review.
8. Move to Dynamixel TTL interface only after power sheet reaches REVIEW.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use Radxa ZERO 3W as the primary host | Target MicroDuck DIY compute module |
| 2026-09-09 | Direct 40-pin HAT connection | Avoid unnecessary adapter PCB |
| 2026-09-09 | Dynamixel TTL is mandatory | XL330 target actuators use TTL bus |
| 2026-09-09 | RS-485 is optional/DNP-capable | Not required for core MicroDuck actuator set |
| 2026-09-09 | Retain audio in V1 scope | Microphone and speaker are desired robot functions |
| 2026-09-09 | Prefer 4-layer PCB | Better ground integrity, power distribution and noise control |
| 2026-09-09 | Use regulated 5 V high-current external input for V1 | Both Radxa ZERO 3W and XL330 are 5 V-class devices; avoids an impractical 20+A onboard buck |
| 2026-09-09 | Keep servo and host current paths physically separated | Reduce servo-induced host voltage sag/noise |
| 2026-09-09 | Use TPS25947 as the leading host eFuse candidate | 5.5 A class with true reverse-current blocking and protection features |
| 2026-09-09 | Keep configurable host reverse-current protection in prototype | USB-C and HAT 5 V coexistence must be proven before simplification |
| 2026-09-09 | Do not fabricate until explicit design review | Power and connector mistakes can damage Radxa/servos |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.3-dev` - MicroDuck-specific 5 V power architecture, current budget and first component candidates established. **Not fabrication-ready.**
