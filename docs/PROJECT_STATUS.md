# Project status

Last updated: 2026-09-13

## Current phase

**Stage 2 integrated — exact J4 model restored locally; 4 mm host-stack CAD interference found; Stage 1 and Qwiic parity preserved; fabrication approval pending**

### CI and online CAD follow-up

- Fixed the locally reproduced Linux CI setup failure by explicitly installing
  pinned KiCad symbols/footprints and initializing their global library tables.
- Fixed a second Linux export failure: accept only the exact pinned Ubuntu
  KiCad build suffix in generated Gerber/drill timestamp normalization; unknown
  versions remain rejected. Added RED/GREEN regression coverage.
- Current-source native strict-port checks pass on Windows and the reproduced
  Ubuntu environment. Parent verification also passed Stage 1/2 acceptance,
  mutation/parity/artwork checks, the three local J4 model checks, and synthetic
  amplifier-overlay compile/apply. Manufacturing unit run: 27 tests, 2 integration
  tests skipped. This does not claim a current clean-commit release integration
  pass. Linux pcbnew emitted nonfatal enum-initialization assertions.
- At that initial local checkpoint no commit/push had been made. Subsequent
  pre-commit review and finding validation are recorded in `14_CODE_REVIEW_CLOSURE.md`;
  the exact published commit's GitHub checks remain the source for remote CI status.
- Exact CAD rejects the assumed 4.0 mm host stack: J4 body interference,
  C7/USB-C nominal model distance 0.005 mm, and a maximum-dimensional C45
  envelope distance of 0.465 mm. See `../mechanical/CAD_REPORT.md`.

### Connector / spacer follow-up

- Executed source-bound CAD comparisons at seven gaps, 4.0 through 10.0 mm;
  see `../mechanical/STACK_REVIEW.md` and `stack_sweep.json` in that directory.
- 4.0 mm remains mechanically rejected. At 6.2 mm the nominal socket-body
  separation is only 0.0074 mm, below its body-height tolerance; do not adopt it.
- 6.5/7/8 mm body separation does not establish permitted insertion. 9/10 mm
  are supplier-confirmation candidates only, not selected spacers. Current
  B.Cu socket is approached from its exposed face, unlike the supplier's
  top-of-HAT bottom-entry example. Exact -01 entry/insertion approval is open.
- Toby names THD-20-R as a REF-family mate; this does not identify the actual
  Radxa header. The user-supplied official ZERO 3W page offers both headered
  and unheadered versions, without resolving the purchased SKU/revision.
- Nominal M2.5 screw fit is not supported at one CAD hole pair after header
  alignment; a smaller shaft is an evaluation option, not assembly approval.
- An unsent supplier/assembler request is prepared in
  `../mechanical/STACK_APPROVAL_REQUEST.md`. No PCB, schematic, BOM/PnP,
  existing package or manufacturing approval was changed.

## Architecture

- Active board count: **1**
- Active PCB: `hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb`
- Outline: 65.00 × 30.90 mm on the Edge.Cuts centerline (approximately 65 × 31 mm)
- Copper layers: 4
- Footprints: 133
- Routed tracks and vias: 1,396
- Daughterboard: **none**
- Archived divergent split design: `archive/v027-split-hat` at `2f2afd8`

## Completed

- [x] Preserved the split design as an archive branch.
- [x] Restarted from the last pre-split commit on `refactor/strict-radxa-port`.
- [x] Imported the complete upstream schematic hierarchy, KiCad project and routed PCB from upstream commit `23eab11927f95ceca0dfa35bf182caeb7db39ea0`.
- [x] Renamed the project and visible board identity for the Radxa derivative.
- [x] Replaced critical Raspberry Pi BCM net names with Radxa physical-interface functions:
  - pins 3/5: I2C3 M0
  - pins 8/10: UART2 M0
  - pins 12/35/38/40: I2S3 M0
- [x] Retained the upstream single-board power, Dynamixel, sensor and audio architecture.
- [x] Kept the upstream HAT EEPROM DNP.
- [x] Restored J6/J7/J8 and R18/R19/R20/R21/R34/R35/R38/R39 to the upstream populated state.
- [x] Added a compilable Radxa device-tree overlay exposing J6/J7/J8 as independent open-drain `i2c-gpio` aliases 10/11/12 while J5 remains on hardware I2C3 M0.
- [x] Produced a DRC-clean J4 candidate without moving the connector grid or routed tracks; current DRC has zero errors.
- [x] Added C45 10 µF / 50 V X7R input bypass, corrected C21/C22 to their actual 10 V MPN rating, rerouted only the local U9/D1/C22 region, and regenerated the GND zone with zero new DRC/parity findings.
- [x] Added a bottom-silkscreen one-source warning prohibiting simultaneous USB-C and HAT battery power.
- [x] Overlaid the HAT against official Radxa V1.11 DXF/STEP/placement resources; electrical alignment is established and remaining physical/RF gates are documented.[4][5][6]
- [x] Vendored 12 exact project-local footprints and `fp-lib-table` without changing the PCB; current native DRC has zero findings and ERC footprint-link warnings are eliminated.
- [x] Fixed the order stackup at 1.0 mm, 70/35/35/70 µm copper and ENIG, with a fail-closed stackup hash.
- [x] Added and test-executed a deterministic manufacturing-package generator with DNP/BOM/PnP/Gerber/drill/PDF/hash validation.
- [x] Captured upstream and adapted ERC/DRC/netlist reports under `validation/strict_port/`.
- [x] Applied Stage 1: Q2 DMN3023L-7 with exact suggested land, R8.1 battery bias for U10 VS, and C39 CL05B104KB5NNNC 100 nF/50 V. Added a thirteenth vendored footprint and exact topology/identity/geometry regression tests; active native DRC and existing functional-parity tests pass.

## Native KiCad baseline

**Current Stage 2:** 134 components / 98 nets, 133 footprints / 1,396 tracks and
vias, 0 DRC violations / 0 unconnected, 46 inherited ERC warnings and 105
Datasheet parity warnings. Full/populated BOM rows are 130/121; complete
full/populated board-position rows are 133/124, including THT connectors and
test features (not a direct SMT machine feed). Drill totals are 150 PTH / 42 NPTH.
See `13_STAGE2_GPIO_AUDIO_CLOSURE.md`; paragraphs below retain milestone history.

The following baseline paragraph describes the pre-Stage-1 milestone. Current
Stage 1 has the same component/net/ERC/DRC totals, but **108** inherited
Datasheet parity warnings after correcting Q2/C39 metadata, and **1,019**
tracks/vias. The later J4/C45 history below likewise records 1,013 at that older
milestone. Current machine-checked totals are in `validation/strict_port/report_summary.json`.

The upstream project produces a parseable 128-component / 95-net schematic netlist; the adapted port has 127 components / 95 nets after adding exact input-bypass capacitor C45 and removing the non-electrical H2/H3 Pollen Robotics and Hugging Face logo symbols. Upstream has 55 ERC warnings. The port has 46: eight footprint-link warnings and two logo-symbol library warnings are resolved, while one exact `lib_symbol_mismatch` for C45 remains explicitly approved pending symbol-library cleanup. The upstream PCB baseline has 49 DRC findings: 40 J4 hole-clearance errors and 9 library-footprint warnings. The adapted PCB resolves all 49 and has zero DRC findings. KiCad's explicit schematic-parity check reports 110 remaining inherited `Datasheet` field mismatches after the J4 manufacturing identity correction resolves one upstream mismatch. No finding was waived or excluded.

These totals use a pinned validation policy. Four ERC categories (`footprint_filter`, `four_way_junction`, `simulation_model_issue`, `single_global_label`) and seven DRC categories (`footprint_filters_mismatch`, `footprint_type_mismatch`, `missing_courtyard`, `npth_inside_courtyard`, `pth_inside_courtyard`, `track_not_centered_on_via`, `tuning_profile_track_geometries`) are ignored exactly as in the imported project. CI fails if the ignored list, rule severities, constraints or exclusions change.

## J4 fabrication correction

J4 is an SMT bottom-entry, pass-through 2×20 socket family intended for Raspberry Pi HAT applications.[1] The supplier drawing identifies the REF-182665-01 2×20 Tiger Beam socket assembly and its 2.54 mm pitch construction.[2] A comparable production connector is also documented as a low-profile SMT GPIO socket for HAT use.[3]

The schematic and PCB manufacturing fields now name only `Toby Electronics REF-182665-01`. The stale `THD-20-R` mating-header identity and non-equivalent LCSC `C2685112` socket identifier were removed so BOM export cannot silently select the wrong connector. The modified land still requires vendor/assembler approval or representative prototype validation before fabrication release.

The imported footprint placed each 1.02 mm NPTH pin passage only 0.02 mm from its associated SMD land, below the project's 0.20 mm hole-clearance rule. The DRC-clean J4 correction keeps all 40 passage holes, the 2.54 mm grid, the pad outer edges and the footprint origin unchanged. At the J4 milestone it did not alter any routed copper. Each 2.00 mm-long land is shortened to 1.80 mm and shifted outward by 0.10 mm, moving only its inner edge by 0.20 mm. KiCad 10.0.6 now measures at least 0.22 mm nominal hole-to-copper clearance and reports no J4 hole-clearance violation. The later C45 power-integrity change locally reroutes copper near U9/D1/C22, bringing the current board total to 1,013 track/via items.

The exact REF-182665-01 supplier drawing does not publish a recommended PCB land pattern. The 1.02 × 1.80 mm candidate is plausible relative to related connector patterns but is not claimed as manufacturer-approved. Connector-vendor or assembly-house signoff—or successful prototype assembly—is therefore still required before fabrication release.

The checker pins the exact J4 footprint S-expression after platform newline and leading-indent normalization, including quoted strings, placement, graphics, pad layers, paste/mask attributes, holes and UUID inventory. It subtracts exactly the 40 known J4 findings from the pinned upstream DRC baseline. Any different removed finding, new finding or J4 footprint text drift fails validation.

## Release blockers

Reference header/pinmux audit: see `15_HOST_PINMUX_REFERENCE_AUDIT.md` and
`validation/strict_port/host_pin_reference_audit.json`. All 40 numbered J4
contacts were enumerated against official V1.11/V1.12 reference publications;
active allocations agree with the selected vendor pinctrl. Native strict-port,
Qwiic parity and synthetic overlay compile/apply/readback checks pass. The
actual host revision and complete image DTB remain unidentified, so the
corresponding release checkboxes below intentionally remain open. Pin 15 is
U11 INT1 through R25, and codec MCLK is the existing HAT Y1 12 MHz oscillator.

- [x] Corrected the gate-drive rating mismatch: Q2 is now DMN3023L-7, rated ±20 V VGS, with manufacturer-suggested pads and unchanged numbered G/S/D connections. Actual VGS, hot-load loss and SOA remain physical gates.
- [x] Moved R8.1 to +BATT for U10 VS and qualified C39's exact 50 V MPN digitally. Assumed battery envelope is 6.0–8.4 V, not a verified pack specification. Measure VS, hot-plug pulse, battery-removal and USB-only behavior before electrical signoff.
- [x] Replaced the raw-battery/Zener GPIO31 path with Q3 host-referenced active-LOW presence sensing; exact part/net/population checks pass. Powered-off leakage/voltage still needs measurement.
- [x] Implemented Q4/Q5 default-OFF SHDN control from J4.11 and the opt-in amplifier overlay. Scope bootloader/codec/power sequencing and verify actual silence before accepting boot-time behavior.
- [ ] Measure battery-input leakage and amplifier enable/shutdown behavior on the actual assembled board and OS image; digital topology is not a physical safety/noise qualification.
- [x] Acquired exact J4 STEP through Samtec's linked public CAD service, verified native locator/lead alignment, installed a project-relative licensed local model, and removed the unrelated socket/Pi references without changing copper/pads/nets. Local models are Git-ignored; clean clones require re-acquisition.
- [ ] Restore exact J1/J2/J9 WAGO models (official published STEP endpoint returns 404), and resolve additional MK1/Y1 model gaps. Current top/bottom renders are explicitly incomplete, not assembly approval.
- [ ] Qualify the complete male-header/J4/spacer stack. Exact CAD shows major body interference at the earlier 4.0 mm gap; the 6.2 mm diagnostic case is not an approved alternative. See `../mechanical/j4_evidence.json`.
- [ ] Obtain connector-vendor/assembly-house approval for the J4 1.02 × 1.80 mm DRC-clean land pattern, or validate it on a representative assembled prototype.
- [ ] Independently verify every critical J4 pin against the exact Radxa ZERO 3W hardware revision.
- [ ] Validate the `i2c3m0_xfer` overlay and document the effect of disabling/reassigning the FUSB302 I2C3 M1 device.
- [ ] On the intended OS image, verify `CONFIG_I2C_GPIO`, enumerate J6/J7/J8 as I2C buses 10/11/12, and complete an address scan plus read/write transfer on each port.
- [ ] Disable UART2 console/getty and validate 1 Mbps Dynamixel traffic.
- [ ] Validate I2S3 codec capture/playback and clocking.
- [ ] Validate the documented 2 A operating envelope: 8 Ω speakers, muted boot, measured audio limit, startup/load-step voltage and 30-minute U9/L4/Q2 thermal test.
- [ ] Keep USB-C and HAT battery power mutually exclusive; complete both source-order reverse-current tests before changing this restriction.
- [ ] After qualifying the full connector stack, measure at least 0.5 mm residual clearance at C45/Radxa U1 on every intended SKU. The earlier 4.0 mm C45-only gap proposal fails J4 body clearance; include C45's 2.5 +/-0.2 mm thickness tolerance.[5][6]
- [ ] Use the external U.FL antenna or complete OTA validation; the full-size copper HAT has no approved onboard-antenna keepout.[7]
- [ ] Verify USB-C, micro-HDMI, microSD and CSI access with nominated cables/FPC and the controlled spacer stack; optional heatsinks remain unsupported until overlaid.

- [x] Reconciled BOM/position outputs with the upstream production release: the exact upstream DNP set remains `C25/R10/R11/R16/R17/R36/R37/R41/U4`, with 114 populated BOM rows and 110 populated PnP rows after removing the H2/H3 logo artifacts. A clean-snapshot candidate passes deterministic package reproduction. The older `production/releases/89a7d5a2/` package still contains the removed front-silkscreen artwork and must not be used; only a verified commit-keyed package generated from the logo-free source commit may be ordered. Every package remains `fabrication_ready=false`.
- [x] Corrected the BOM exporter's mixed manufacturer-field handling and added exact J4 purchasing-identity and population guards. Fresh native full/populated BOM regression passes. Historical `production/releases/7f1aef08/` BOMs still have blank J4 purchasing columns and are not assembly-order inputs.
- [x] Closed the former candidate's 3 unconnected items and 14 physical warnings, merged with Stage 1, and retained all connectors. The older unintegrated temporary candidate and previous release packages are superseded; see `13_STAGE2_GPIO_AUDIO_CLOSURE.md`.
- [ ] Close the remaining electrical and 3D digital-review blockers above. Prior functional-parity and ERC/DRC passes remain valid within their scope, but do not constitute complete electrical or mechanical approval.

## Release status

The architecture is now aligned with the original project: a single routed Robot HAT adapted at the host interface for Radxa ZERO 3W. It is **not fabrication-ready** until the blockers above are closed.

## Sources

[1] https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets — Toby REF Raspberry Pi HAT SMT sockets
[2] https://www.toby.co.uk/storage/documents/1540.pdf — Samtec REF-182665-01 drawing package
[3] https://www.adafruit.com/product/2187 — Adafruit SMT GPIO Header for Raspberry Pi HAT
[4] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_2d_dxf.zip — Radxa ZERO 3W V1.11 DXF
[5] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_3d_stp.zip — Radxa ZERO 3W V1.11 STEP
[6] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1110_smb.zip — Radxa ZERO 3W V1.11 placement maps
[7] https://docs.radxa.com/en/zero/zero3/accessories/zero3w-antenna — Radxa ZERO 3W antenna instructions
