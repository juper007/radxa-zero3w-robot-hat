# Radxa ZERO 3W Mechanical and RF Review

## Current CAD correction — 2026-09-13

The exact J4 `REF-182665-01` STEP has now been acquired, aligned to its PCB
locator holes, installed as a licensed local model, and rendered. The unrelated
FH-00339 socket and Raspberry Pi host model references have been removed from
the active PCB and vendored J4 footprint. No pad, hole, net or copper changed.
See `../hardware/kicad/LOCAL_3D_MODELS.md`, `../mechanical/J4_PLACEMENT.md`,
and `../validation/mechanical/model_only_change_audit.json`.

**The previously proposed 4.0 mm gap is NOT a valid whole-assembly approval.**
Actual CAD intersection with the official Radxa host shows major J4/host-header
body interference at that gap. The 6.2 mm diagnostic case is not an approved
alternative: header MPN, insertion/contact geometry, tolerances and physical
seating remain unqualified. See `../mechanical/j4_evidence.json` for computed
solid intersections. Do not order spacers from the earlier 4.0 mm value alone.

The older outline/C45 discussion below is retained as the review history.
Its approximate XY transform is superseded for current CAD work by the
header-grid-derived transform documented in `../mechanical/HANDOFF.md`.
Supplier C45 thickness is 2.5 +/-0.2 mm; a nominal-height render cannot
establish worst-case 0.5 mm residual clearance.

The wider underside check also finds **C7 only 0.005 mm from the official
host's USB-C body model at the 4.0 mm gap**. C45 nominal CAD separation is
0.665 mm, but its explicitly labeled maximum-dimensional envelope reduces this
to 0.465 mm. These are calculated model distances, not measured physical gaps.
The current header-aligned CAD transform also leaves up to 0.269105 mm mounting
axis mismatch. Detailed evidence, source hashes and limitations are in
`../mechanical/CAD_REPORT.md`; no spacer length or complete screw fit is approved.

## Scope and source revision

This review overlays the current one-board HAT against Radxa's official ZERO 3W V1.11 DXF and STEP resources.[1][2][3]

The official component-placement map is used as a second overlay reference.[4]

The V1.12 AIC8800 schematic represents a later radio variant, so every intended SKU still requires first-article inspection.

## Board and mounting alignment

Current HAT Edge.Cuts centerline:

- X: `70.8975–135.8975 mm`
- Y: `75.2400–106.1400 mm`
- size: `65.000 × 30.900 mm`

Current mounting-hole centers:

- `(74.4025, 79.6350)`
- `(132.4025, 79.6350)`
- `(74.4025, 102.6350)`
- `(132.4025, 102.6350)`

The hole rectangle is `58 × 23 mm`. Hole-aligned comparison to the official STEP establishes the valid, non-rotated GPIO orientation. A 180° overlay is invalid because it reverses J4 pin numbering.

The official Radxa STEP envelope is approximately `65.0016 × 30.0055 mm`.[3] The HAT therefore extends approximately 0.9 mm beyond the host on one long edge when the hole patterns are aligned. This does not by itself cause a collision, but enclosure and cable clearances must use the larger HAT envelope.

## C45 clearance

C45 is a nominal `3.2 × 2.5 × 2.5 mm` 1210 MLCC on HAT B.Cu at `(99.05, 100.95)`. The hole-aligned transform is:

```text
Xradxa = Xhat - 70.9025
Yradxa = 106.135 - Yhat
```

C45 maps to approximately Radxa `(28.1475, 5.1850)`. Its XY projection overlaps the official STEP's central U1/RK3566 package region, whose local top-side envelope is approximately 0.8 mm above the Radxa PCB.[3][4]

The layout is therefore electrically accepted but mechanically conditional. Release requires all of the following:

1. A qualified complete header/socket/spacer stack; `4.0 mm` was a C45-only lower-bound proposal and fails the exact J4/host-body CAD check above.
2. Measured residual physical clearance of at least `0.5 mm`.
3. Controlled M2.5 spacers; connector friction must not set the gap.
4. Repeat inspection for every intended ZERO 3W SKU.
5. Center-load and thermal-cycle checks with no witness mark, rocking, bow or intermittent contact.
6. If these checks fail, hold assembly. Qualify a lower-height or relocated input bypass capacitor and re-run electrical/physical checks; simply omitting C45 is not an approved production workaround.

## J4 connector stack

J4 is on B.Cu at `(103.3975, 79.64)`, rotation `-90°`. Its mounting-hole and electrical grids align with the host, but the exact assembled Z-stack is not defined by the PCB source. Toby documents REF-182665-01 as a pass-through, bottom-entry HAT socket with a finite insertion-depth range.[6]

Before fabrication release, the assembly drawing must define:

- exact male-header and socket MPNs;
- PCB-surface spacing and M2.5 spacer length;
- minimum and maximum pin insertion;
- connector body orientation;
- first-article continuity and mechanical fit.

This gate is shared with the modified J4 land-pattern signoff.

### Exact model and land-pattern handoff

The exact J4 model is now installed with a project-relative reference into
Git-ignored `models-local/`, and its locator/lead alignment was checked through
native STEP export. A clean clone must re-acquire the licensed model. The old
Raspberry Pi and non-equivalent socket references are removed, not substituted
with a visually similar model. All required connectors remain populated.

J1/J2/J9 (WAGO `2059-302/998-403`) still require exact-model acquisition and
placement. WAGO's public exact-MPN MCAD record is available, but its published
STEP file endpoint returned 404. The complete inventory also identified
unresolved MK1 and Y1 models. Missing render bodies are not DNP decisions.

Required digital closure before accepting a complete assembly render:

1. Obtain remaining exact WAGO/MK1/Y1 models with permitted use. Toby's page
   requires login, but exact J4 was acquired via Samtec's linked public CAD service.
2. Keep restricted standalone models local; retain source/MPN/hash provenance and
   project-relative paths. Use the actual Radxa STEP as the assembly reference.
3. Verify lead positions and pin 1 against copper, and body heights against the
   supplier drawing. A resolved file path alone is not mechanical validation.
4. Both current board sides have been rendered; complete the missing bodies and
   qualify the host stack before treating a render as complete mechanical evidence.

The current J4 lands are `1.02 x 1.80 mm`, with at least `0.22 mm` nominal copper
clearance to the preserved NPTH holes. The exact supplier drawing does not give
a recommended PCB land/paste pattern. Send the exact drawing, land dimensions,
board thickness and assembly process to the vendor/assembler for approval; do
not infer solder-joint approval from zero DRC or from a related-family footprint.

These are **exact-model access / external assembly approval** gates, not a
claim that the existing parts necessarily collide.

## External interfaces

The two USB-C ports, micro-HDMI, microSD and CSI connector are on the host perimeter in the official mechanical data.[2][3][4] Lateral access is plausible but not approved from bare-board overlap alone.

Required first-article checks:

- both nominated USB-C cable overmolds;
- micro-HDMI overmold and strain relief;
- microSD insertion, removal and fingernail/tool access;
- CSI latch operation and FPC minimum bend radius;
- access while the HAT is fully screwed down at the controlled gap;
- any enclosure wall or cable-retention feature.

No optional heatsink envelope is approved. A heatsink is incompatible until its exact STEP is included in the assembly overlay.

## Antenna policy

Radxa documents an onboard antenna and an external U.FL antenna option.[5] The full-size HAT contains copper above the host and no validated onboard-antenna keepout. The onboard antenna may therefore be detuned or shielded.

Release must choose one of these paths:

- default to the external U.FL antenna mode; or
- define a quantified HAT copper keepout and pass conducted/OTA range validation with the final enclosure.

The current release recommendation is **external U.FL antenna**.

## Verdict

- Hole/grid alignment: **historical overlay only; current CAD datum/tolerance qualification required**
- Board outline compatibility: **conditional — 0.9 mm long-edge overhang**
- C45 physical clearance: **conditional — qualified stack and measured 0.5 mm residual required; include component tolerance**
- J4 model restoration: **locally complete; native locator/lead alignment checked**
- J4 Z-stack: **4.0 mm case fails CAD body interference; no alternate stack approved**
- USB-C/HDMI/microSD/CSI access: **first-article check required**
- Onboard antenna under HAT: **not approved**
- External U.FL antenna: **recommended**
- Optional heatsink: **not approved without exact overlay**
- Fabrication-ready: **no**

## Sources

[1] https://docs.radxa.com/en/zero/zero3/download — Radxa ZERO 3 resource download
[2] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_2d_dxf.zip — Radxa ZERO 3W V1.11 DXF
[3] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_3d_stp.zip — Radxa ZERO 3W V1.11 STEP
[4] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1110_smb.zip — Radxa ZERO 3W V1.11 placement maps
[5] https://docs.radxa.com/en/zero/zero3/accessories/zero3w-antenna — Radxa ZERO 3W antenna instructions
[6] https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets/REF-182665-01 — Toby REF-182665-01 connector
