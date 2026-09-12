# Project status

Last updated: 2026-09-11

## Current phase

**v0.19-strict-port — upstream single-board design imported and host-net adaptation applied; review and release validation pending**

## Architecture

- Active board count: **1**
- Active PCB: `hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb`
- Outline: 65.00 × 30.90 mm on the Edge.Cuts centerline (approximately 65 × 31 mm)
- Copper layers: 4
- Footprints: 127
- Routed tracks: 1,021
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
- [x] Marked auxiliary Pi-specific Qwiic connectors J6/J7/J8 and isolation/pull-up resistors R18/R19/R20/R21/R34/R35/R38/R39 DNP.
- [x] Produced a DRC-clean J4 candidate without moving the connector grid or routed tracks; current DRC has zero errors.
- [x] Captured upstream and adapted ERC/DRC/netlist reports under `validation/strict_port/`.

## Native KiCad baseline

The upstream project and adapted port both produce a parseable 128-component / 95-net schematic netlist. Each has the same 55 inherited ERC warnings: 42 library-symbol mismatches, 8 footprint-link issues and 5 library-symbol issues. The upstream PCB baseline has 49 DRC findings: 40 J4 hole-clearance errors and 9 library-footprint warnings. The adapted PCB resolves the 40 J4 errors and retains only the 9 warnings. KiCad's explicit schematic-parity check reports 110 remaining inherited `Datasheet` field mismatches after the J4 manufacturing identity correction resolves one upstream mismatch. None of the remaining inherited warnings has been waived or excluded, and no new ERC/DRC/parity findings were introduced.

These totals use a pinned validation policy. Four ERC categories (`footprint_filter`, `four_way_junction`, `simulation_model_issue`, `single_global_label`) and seven DRC categories (`footprint_filters_mismatch`, `footprint_type_mismatch`, `missing_courtyard`, `npth_inside_courtyard`, `pth_inside_courtyard`, `track_not_centered_on_via`, `tuning_profile_track_geometries`) are ignored exactly as in the imported project. CI fails if the ignored list, rule severities, constraints or exclusions change.

## J4 fabrication correction

J4 is an SMT bottom-entry, pass-through 2×20 socket family intended for Raspberry Pi HAT applications.[1] The supplier drawing identifies the REF-182665-01 2×20 Tiger Beam socket assembly and its 2.54 mm pitch construction.[2] A comparable production connector is also documented as a low-profile SMT GPIO socket for HAT use.[3]

The schematic and PCB manufacturing fields now name only `Toby Electronics REF-182665-01`. The stale `THD-20-R` mating-header identity and non-equivalent LCSC `C2685112` socket identifier were removed so BOM export cannot silently select the wrong connector. The modified land still requires vendor/assembler approval or representative prototype validation before fabrication release.

The imported footprint placed each 1.02 mm NPTH pin passage only 0.02 mm from its associated SMD land, below the project's 0.20 mm hole-clearance rule. The DRC-clean candidate keeps all 40 passage holes, the 2.54 mm grid, the pad outer edges, the footprint origin and all 1,021 tracks unchanged. Each 2.00 mm-long land is shortened to 1.80 mm and shifted outward by 0.10 mm, moving only its inner edge by 0.20 mm. KiCad 10.0.6 now measures at least 0.22 mm nominal hole-to-copper clearance and reports zero J4 clearance errors.

The exact REF-182665-01 supplier drawing does not publish a recommended PCB land pattern. The 1.02 × 1.80 mm candidate is plausible relative to related connector patterns but is not claimed as manufacturer-approved. Connector-vendor or assembly-house signoff—or successful prototype assembly—is therefore still required before fabrication release.

The checker pins the exact J4 footprint S-expression after platform newline and leading-indent normalization, including quoted strings, placement, graphics, pad layers, paste/mask attributes, holes and UUID inventory. It subtracts exactly the 40 known J4 findings from the pinned upstream DRC baseline. Any different removed finding, new finding or J4 footprint text drift fails validation.

## Release blockers

- [ ] Obtain connector-vendor/assembly-house approval for the J4 1.02 × 1.80 mm DRC-clean land pattern, or validate it on a representative assembled prototype.
- [ ] Independently verify every critical J4 pin against the exact Radxa ZERO 3W hardware revision.
- [ ] Validate the `i2c3m0_xfer` overlay and document the effect of disabling/reassigning the FUSB302 I2C3 M1 device.
- [ ] Disable UART2 console/getty and validate 1 Mbps Dynamixel traffic.
- [ ] Validate I2S3 codec capture/playback and clocking.
- [ ] Demonstrate AP63205 2 A worst-case load, startup-transient, voltage-drop and thermal margin for the Radxa host plus HAT loads.
- [ ] Review simultaneous USB-C/HAT 5 V power and backfeed behavior.
- [ ] Overlay authoritative Radxa mechanical data and inspect USB-C, HDMI, microSD, CSI and antenna clearances.
- [ ] Resolve or formally disposition the 9 remaining inherited library-footprint DRC warnings.
- [ ] Reconcile the derivative BOM/position outputs with the upstream production release.
- [ ] Perform an independent schematic, polarity, footprint and connector review.

## Release status

The architecture is now aligned with the original project: a single routed Robot HAT adapted at the host interface for Radxa ZERO 3W. It is **not fabrication-ready** until the blockers above are closed.

## Sources

[1] https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets — Toby REF Raspberry Pi HAT SMT bottom-entry sockets
[2] https://www.toby.co.uk/storage/documents/1540.pdf — Samtec/Toby REF-1826xx connector drawing
[3] https://www.adafruit.com/product/2187 — Adafruit SMT GPIO Header for Raspberry Pi HAT
