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
- [x] Separated servo and Radxa current paths
- [x] USB-C / HAT backfeed identified as mandatory validation item
- [x] TPS25947 selected as host-branch eFuse/reverse-current candidate
- [x] Main reverse-protection controller selected: LM74700-Q1 candidate
- [x] Main low-RDS MOSFET selected: BSC009NE2LS5I candidate
- [x] V1 input connector direction moved to XT60-class/pigtail for prototype margin
- [x] 10 A / 15 A / 20 A copper-loss calculations completed
- [x] 2 oz outer copper preferred for high-current prototype
- [x] Three nominal 5-servo power branches defined
- [x] V1 power connectivity table created

## Key electrical numbers

- XL330-M288-T input voltage: 5 V
- XL330-M288-T stall current at 5 V: ~1.47 A
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa official recommended supply: >=15 W at 5 V (>=3 A source capability)
- Provisional Radxa/audio/logic allocation: ~4 A branch target
- Pathological total envelope: ~26 A
- Recommended development supply: regulated 5 V, 15–20 A class
- BSC009NE2LS5I conservative RDS(on) used: 1.35 mΩ @ 4.5 V gate
- Estimated Q1 loss at 20 A: ~0.54 W

## Current component decisions

| Function | V1 direction |
|---|---|
| Main input | regulated 5 V |
| Main connector | XT60-class / heavy pigtail |
| Main reverse protection | LM74700-Q1 + BSC009NE2LS5I |
| Main fuse | 20 A class provisional |
| Servo distribution | 3 branches × 5 servos nominal |
| Host protection | TPS25947 family |
| Outer copper | 2 oz preferred |
| Main routing | wide polygon pours + multilayer sharing |

## In progress

- [ ] Freeze exact TPS25947 ordering suffix
- [ ] Calculate TPS25947 ILIM resistor
- [ ] Calculate TPS25947 dV/dt capacitor
- [ ] Freeze OVLO/OVC behavior for 5 V Radxa branch
- [ ] Select fuse holder/package
- [ ] Select exact XT60/pigtail footprint geometry
- [ ] Implement actual `hardware/kicad/power.kicad_sch`
- [ ] Run KiCad ERC

## Next actions

1. Freeze TPS25947 suffix and programming network from TI datasheet.
2. Translate `power_v1_connectivity.csv` into KiCad symbols/wires/net labels.
3. Add LM74700 reference circuitry and charge-pump components.
4. Assign provisional footprints.
5. Run ERC.
6. Review current path and connector placement.
7. Move the power subsystem to REVIEW only after schematic checks pass.
8. Start Dynamixel TTL interface after power sheet is stable.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use Radxa ZERO 3W as the primary host | Target MicroDuck DIY compute module |
| 2026-09-09 | Direct 40-pin HAT connection | Avoid unnecessary adapter PCB |
| 2026-09-09 | Dynamixel TTL is mandatory | XL330 target actuators use TTL bus |
| 2026-09-09 | RS-485 is optional/DNP-capable | Not required for core MicroDuck actuator set |
| 2026-09-09 | Retain audio in V1 scope | Microphone and speaker are desired robot functions |
| 2026-09-09 | Prefer 4-layer PCB | Better ground integrity, power distribution and noise control |
| 2026-09-09 | Use regulated 5 V high-current external input for V1 | Radxa and XL330 are both 5 V devices; avoid high-power onboard buck |
| 2026-09-09 | Keep servo and host current paths physically separated | Reduce servo-induced host voltage sag/noise |
| 2026-09-09 | Use TPS25947 family for host branch | True reverse-current blocking and 5.5 A-class protection |
| 2026-09-09 | Use LM74700-Q1 + low-RDS external FET for main path | Integrated 5.5 A eFuse is insufficient for servo rail |
| 2026-09-09 | Use BSC009NE2LS5I as first main MOSFET candidate | 25 V, ~1.35 mΩ max at 4.5 V, compact power package |
| 2026-09-09 | Use XT60-class input for V1 prototype | More margin for >20 A pathological servo current than XT30 |
| 2026-09-09 | Prefer 2 oz outer copper | Reduce high-current copper loss and temperature rise |
| 2026-09-09 | Do not fabricate until explicit design review | Power and connector mistakes can damage Radxa/servos |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.4-dev` - main high-current protection, connector direction, copper strategy and schematic connectivity are established. **Not fabrication-ready.**
