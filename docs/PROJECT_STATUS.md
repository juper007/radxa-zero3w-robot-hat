# Project status

Last updated: 2026-09-11

## Current phase

**v0.19-strict-port — upstream single-board design imported and host-net adaptation applied; review and release validation pending**

## Architecture

- Active board count: **1**
- Active PCB: `hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb`
- Outline: 65.05 × 30.95 mm
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
- [x] Marked auxiliary Pi-specific Qwiic connectors J6/J7/J8 DNP.
- [x] Captured upstream and adapted ERC/DRC/netlist reports under `validation/strict_port/`.

## Native KiCad baseline

The upstream project and adapted port both produce a parseable 128-component / 95-net schematic netlist. Each has the same 55 inherited ERC warnings: 42 library-symbol mismatches, 8 footprint-link issues and 5 library-symbol issues. The upstream PCB baseline has 49 DRC findings: 40 hole-clearance errors and 9 library-footprint warnings. KiCad's explicit schematic-parity check also reports the same 111 inherited `Datasheet` field mismatches on both designs. No ERC, DRC or parity finding was introduced by the Radxa adaptation, but all inherited findings remain fabrication blockers.

## Release blockers

- [ ] Independently verify every critical J4 pin against the exact Radxa ZERO 3W hardware revision.
- [ ] Validate the `i2c3m0_xfer` overlay and document the effect of disabling/reassigning the FUSB302 I2C3 M1 device.
- [ ] Disable UART2 console/getty and validate 1 Mbps Dynamixel traffic.
- [ ] Validate I2S3 codec capture/playback and clocking.
- [ ] Review simultaneous USB-C/HAT 5 V power and backfeed behavior.
- [ ] Overlay authoritative Radxa mechanical data and inspect USB-C, HDMI, microSD, CSI and antenna clearances.
- [ ] Resolve or formally disposition all 49 inherited DRC findings.
- [ ] Reconcile the derivative BOM/position outputs with the upstream production release.
- [ ] Perform an independent schematic, polarity, footprint and connector review.

## Release status

The architecture is now aligned with the original project: a single routed Robot HAT adapted at the host interface for Radxa ZERO 3W. It is **not fabrication-ready** until the blockers above are closed.
