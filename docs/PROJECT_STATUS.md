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
- [x] TPS25947 RILM frozen to 825R (~4.05 A calculated typical target)
- [x] TPS25947 dVdt capacitor frozen to 3.9 nF (~9.75 ms 5 V ramp target)
- [x] TPS25947 OVLO divider frozen to 374k / 100k (~5.69 V nominal)
- [x] LM74700 support values frozen: VCAP 100 nF, local input 22 nF minimum, local output 100 nF minimum
- [x] Power connectivity CSV updated to implementation-level values
- [x] Initial KiCad 9 `hardware/kicad/power.kicad_sch` source skeleton created
- [x] Schematic-value design note `docs/05D_POWER_SCHEMATIC_VALUES.md` created
- [x] LM74700 DBV 6-pin package pin map independently re-verified
- [x] BSC009NE2LS5I source/gate/drain package pin map independently re-verified
- [x] TPS259470A RPW 10-pin pin map independently re-verified
- [x] Corrected earlier Q1 source/drain orientation error in connectivity table
- [x] Project-local KiCad symbol library created for U1/U2/Q1
- [x] Project `sym-lib-table` created
- [x] Automated connectivity sanity checker added
- [x] GitHub Actions power-design sanity check executed successfully
- [x] Pinout/library review documented in `docs/05E_POWER_PINOUT_AND_LIBRARY_REVIEW.md`

## Key electrical numbers

- XL330-M288-T supply: 5 V
- XL330-M288-T stall current at 5 V: ~1.47 A
- 15-servo theoretical simultaneous stall: ~22.05 A
- 5-servo branch theoretical stall: ~7.35 A
- Radxa/audio/logic design branch target: ~4 A
- Pathological total envelope: ~26 A
- Development supply: regulated 5 V, 15–20 A class
- TPS259470A nominal host current-limit target: ~4.05 A calculated typical
- Host startup ramp target: ~9.75 ms
- Host OVLO target: ~5.69 V nominal

## Verified package pin maps

### LM74700QDBVRQ1, DBV 6-pin

1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE.

Ideal-diode topology rule: LM74700 ANODE -> external N-MOSFET SOURCE/input side; LM74700 CATHODE -> external N-MOSFET DRAIN/output side.

### BSC009NE2LS5I

Pins 1/2/3 SOURCE, pin 4 GATE, pins 5/6/7/8 DRAIN.

### TPS259470ARPWR

1 EN/UVLO, 2 OVLO, 3 AUXOFF, 4 FLT, 5 IN, 6 OUT, 7 DVDT, 8 GND, 9 ILM, 10 ITIMER.

## Current implementation state

The power topology, component values and critical device pin maps are now frozen at first-pass design level. `hardware/libraries/radxa_robot_hat_power.kicad_sym` contains project-specific symbols and `hardware/kicad/sym-lib-table` registers the library.

`power.kicad_sch` still remains a **structured schematic skeleton** rather than the final electrically wired sheet. It must not be treated as fabrication-ready. The authoritative connectivity is `hardware/kicad/power_v1_connectivity.csv`.

The repository now includes `hardware/kicad/check_power_design.py` and `.github/workflows/power-design-check.yml`. The first GitHub Actions run completed successfully, validating the critical connectivity invariants represented in the CSV.

## In progress

- [ ] Populate `power.kicad_sch` with actual U1/Q1/U2 symbols and passive components
- [ ] Add wires/net labels for the complete power path
- [ ] Select/verify exact TPS25947 RPW land pattern
- [ ] Select/verify exact BSC009NE2LS5I PG-TDSON-8 land pattern
- [ ] Assign provisional footprints to all passives/connectors
- [ ] Finalize TVS/OVP after transient review
- [ ] Finalize servo branch connector footprints
- [ ] Run actual KiCad ERC with KiCad 9
- [ ] Perform schematic design review

## Next actions

1. Create verified footprint libraries for TPS259470ARPWR and BSC009NE2LS5I using manufacturer package drawings.
2. Replace schematic skeleton notes with electrically connected symbols and net labels.
3. Add XT60/pigtail input, fuse, LM74700/Q1, three servo branches, TPS259470A host branch and test points.
4. Run KiCad ERC in a KiCad 9 environment and resolve warnings intentionally.
5. Independently inspect the final source/drain pad mapping after footprint assignment.
6. Move power sheet to REVIEW only after ERC and schematic review.
7. Start Dynamixel TTL interface once power reaches REVIEW.

## Decision log additions

| Date | Decision | Reason |
|---|---|---|
| 2026-09-09 | Use TPS259470ARPWR | Adjustable OVLO, active current limit, auto-retry, true reverse-current blocking |
| 2026-09-09 | Use 825R RILM | Targets about 4.05 A calculated typical host branch current limit |
| 2026-09-09 | Use 3.9 nF CdVdt | Targets roughly 9.75 ms 0-to-5 V startup ramp |
| 2026-09-09 | Use 374k/100k OVLO divider | Targets roughly 5.69 V nominal host over-voltage trip |
| 2026-09-09 | LM74700 ANODE must connect to Q1 SOURCE and CATHODE to Q1 DRAIN | Verified from TI DBV package/function documentation; fixes earlier draft orientation error |
| 2026-09-09 | Keep custom symbol pin maps documented and CI-check connectivity invariants | Reduce chance of silent power-device pin-map regression |
| 2026-09-09 | Keep first KiCad sheet as DESIGNING until symbols/wires/ERC are complete | Prevent a source skeleton from being mistaken for fabrication-ready hardware |

## Status labels

- **PLANNED** - not started
- **DESIGNING** - active schematic/analysis
- **REVIEW** - implementation exists, verification pending
- **FAB-CANDIDATE** - manufacturing files generated but not validated in hardware
- **VALIDATED** - tested on assembled hardware

## Current release status

`v0.6-dev` - critical power-device pin maps verified, source/drain orientation corrected, custom KiCad symbols added, and automated connectivity sanity checking is passing. **Not fabrication-ready.**
