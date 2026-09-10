# Project Status

Last updated: 2026-09-09

## Current phase

**Phase 1 - Power subsystem detailed design**

## Completed

- [x] Repository initialized and architecture documented
- [x] Radxa ZERO 3W 40-pin mapping established
- [x] XL330-M288-T 15-servo current budget completed
- [x] V1 input frozen to regulated 5 V high-current supply
- [x] Servo and Radxa current paths physically separated
- [x] 2 oz outer copper / wide-pour high-current strategy defined
- [x] Main reverse protection selected: LM74700QDBVRQ1 + BSC009NE2LS5I
- [x] Prototype input direction frozen to XT60-class
- [x] Three nominal 5-servo power branches defined
- [x] Radxa branch device frozen to TPS259470ARPWR
- [x] TPS25947 RILM frozen to 825R (~4.05 A typical target)
- [x] TPS25947 dVdt capacitor frozen to 3.9 nF (~9.75 ms 5 V ramp target)
- [x] TPS25947 OVLO divider frozen to 374k / 100k (~5.69 V nominal)
- [x] LM74700 support values frozen: VCAP 100 nF, local input 22 nF minimum, local output 100 nF minimum
- [x] Power connectivity CSV updated to implementation-level values
- [x] Initial KiCad 9 `hardware/kicad/power.kicad_sch` source skeleton created
- [x] Schematic-value design note `docs/05D_POWER_SCHEMATIC_VALUES.md` created

## Key electrical numbers

- XL330-M288-T supply: 5 V
- XL330-M288-T stall current at 5 V: ~1.47 A
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa/audio/logic design branch target: ~4 A
- Pathological total envelope: ~26 A
- Development supply: regulated 5 V, 15–20 A class
- TPS259470A nominal host current-limit target: ~4.05 A typical
- Host startup ramp target: ~9.75 ms
- Host OVLO target: ~5.69 V nominal

## Current implementation state

The first-pass power topology and component values are frozen. `power.kicad_sch` now exists as a KiCad 9 source file, but it is currently a **structured schematic skeleton** rather than the final electrically wired sheet. The authoritative connectivity is `hardware/kicad/power_v1_connectivity.csv` and the authoritative first-pass values are in `docs/05D_POWER_SCHEMATIC_VALUES.md`.

## In progress

- [ ] Create/import project-local symbols for LM74700QDBVRQ1, BSC009NE2LS5I and TPS259470ARPWR
- [ ] Populate `power.kicad_sch` with actual symbols and wires
- [ ] Verify physical package pin numbering and MOSFET source/drain orientation
- [ ] Assign provisional footprints
- [ ] Finalize TVS/OVP after transient review
- [ ] Finalize servo branch connector footprints
- [ ] Run KiCad ERC
- [ ] Perform schematic design review

## Next actions

1. Build/import project-local power symbols and footprint mappings.
2. Replace schematic skeleton notes with electrically connected symbols and net labels.
3. Add XT60, fuse, three servo power branches, host eFuse and all test points.
4. Run ERC and resolve warnings intentionally.
5. Independently verify 40-pin pins 2/4 and all protection-device pinouts.
6. Move power sheet to REVIEW only after ERC and design review.
7. Start Dynamixel TTL interface once power reaches REVIEW.

## Decision log additions

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use TPS259470ARPWR | Adjustable OVLO, active current limit, auto-retry, true reverse-current blocking |
| 2026-09-09 | Use 825R RILM | Targets about 4.05 A typical host branch current limit |
| 2026-09-09 | Use 3.9 nF CdVdt | Targets roughly 9.75 ms 0-to-5 V startup ramp |
| 2026-09-09 | Use 374k/100k OVLO divider | Targets roughly 5.69 V nominal host over-voltage trip |
| 2026-09-09 | Keep first KiCad sheet as DESIGNING until symbols/wires/ERC are complete | Prevent a source skeleton from being mistaken for fabrication-ready hardware |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.5-dev` - exact first-pass power values and initial KiCad power source established. **Not fabrication-ready.**
