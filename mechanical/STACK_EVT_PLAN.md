# 9.5 mm J4 stack — representative EVT plan

## Scope and decision

Use a **header-populated Radxa ZERO 3W**, the populated Toby
`REF-182665-01` J4 socket, a controlled nominal **9.5 mm PCB-surface gap**,
and **M2 insulating spacer hardware**. The official Radxa 2x20 header geometry
is the EVT design basis; its exact factory MPN is not a prerequisite.

This plan qualifies a representative mechanical/electrical prototype. It does
not set `fabrication_ready=true`, approve the J4 land/stencil for production, or
replace the electrical, thermal, audio and operating-system EVT gates.

## Digital basis

- Header grid: 2x20 at 2.54 mm, aligned from all 40 official STEP pin tips.
- Official STEP header plastic top: 2.5 mm above the Radxa PCB.
- Official STEP pin tips: 8.5 mm above the Radxa PCB.
- Exact J4 lower face in native HAT export: -3.7776 mm.
- HAT bottom-mask datum: -0.085 mm.
- At a 9.5 mm surface gap:
  - nominal J4 housing clearance above host plastic: **3.3074 mm**;
  - nominal axial entry past the socket lower face: **2.6926 mm**;
  - the entry is inside the published 1.78–3.43 mm family interval, subject to
    physical confirmation for this exact B.Cu orientation.
- M2 has positive ideal radial fit margin at all four source-bound CAD hole
  positions. M2.5 does not at one position after exact header-grid alignment.

The source-bound eight-gap CAD sweep and its regression tests remain the digital
authority. CAD dimensions are not physical measurements.

## Required parts and tools

- Header-populated Radxa ZERO 3W; do not desolder or replace its factory header.
- Assembled Robot HAT with J4 `REF-182665-01` populated.
- Four insulating M2 spacer stacks adjusted to produce a measured 9.5 mm gap.
- M2 screws/nuts/washers whose heads and outside diameters clear both boards.
- Digital caliper or depth gauge, straightedge, magnification, and multimeter.
- Nominated USB-C, micro-HDMI and CSI cables needed for access checks.

Do not infer the PCB gap from a catalog spacer name. Include washers and shims
in the measured stack, and use all four equal controlled stacks.

## Unpowered mechanical procedure

1. Keep the battery and both USB-C power sources disconnected.
2. Inspect J4 solder joints, locator seating, pin passages and pin-1 orientation.
3. Mate the boards without screws. Stop if either housing bottoms, a pin misses a
   passage, or substantial force/bending is required.
4. Install the four M2 spacer stacks finger-tight. A screw must pass freely; do
   not use screw torque to pull misaligned holes or bowed boards into position.
5. Measure the PCB-surface gap next to all four mounting points and record every
   value. The provisional EVT target is **9.5 ±0.2 mm**, with no more than
   **0.2 mm max-to-min spread** across the four locations.
6. Inspect J4 from both ends. Record housing separation, visible pin protrusion,
   connector seating, board rocking and any witness marks.
7. Confirm at least **0.5 mm measured residual clearance** at the C45/Radxa
   overlap and record the closest underside component clearance.
8. Verify access with the nominated USB-C, micro-HDMI, microSD and CSI/FPC parts.
9. Tighten only enough to retain the stack. Record hardware and torque method;
   reject any visible bow, twist, housing contact or loss of the measured gap.

## Unpowered electrical procedure

### 40-pin continuity

1. Keep both boards unpowered. Short the meter probes together, null the meter
   if supported, and record the numeric shorted-lead resistance in
   `STACK_EVT_CONTINUITY.csv`; a meter beep is not a reading.
2. For each pin N, place probe A on the **exposed solder joint/pad of ZERO 3W
   header pin N on the host underside** and probe B on the **exposed outer toe
   of HAT J4 SMT land N**. Do not substitute a shared power/GND point.
3. Record numeric raw resistance and corrected resistance (raw minus the
   recorded shorted-lead resistance) for the initial assembly, bounded-pressure
   check, and post-remate check. Each stage passes only when corrected resistance
   is **<= 1.0 ohm**; do not record only a meter beep or qualitative continuity.
4. Apply only the gentle bounded pressure used by the mechanical check, then
   fully release it. Unmate/remate once before the post-remate measurements.
   A transient or any stage above the limit fails that pin.

### Physical-grid adjacent-pair isolation

1. Use `STACK_EVT_ISOLATION.csv`, whose physical 2x20 grid enumerates **20
   cross-row pairs** `(1,2),(3,4),...,(39,40)`, **19 odd-column pairs**
   `(1,3),...,(37,39)`, and **19 even-column pairs**
   `(2,4),...,(38,40)`: **exactly 58** unique adjacent pairs.
2. Before mating, record the toe-to-toe baseline using the corresponding **J4
   outer toes**. For initial assembled, bounded-pressure, and post-remate
   measurements, probe the corresponding **exposed host underside header solder
   joints**. Record numeric raw and lead-null-corrected resistance, not a beep.
3. For every `distinct_net` pair, wait for an **after 2 s stabilized** reading.
   The hard-short isolation criterion is **> 50 ohm** at every stage and **no
   sustained <= 50 ohm**. Any sustained reading at or below 50 ohm fails.
4. Same-net pairs (`same_net`) are expected-connected and must be marked **N/A**
   in pass fields, not counted as isolation passes. Record unexpected or unstable
   behavior in notes; never treat shared-net connectivity as a distinct-net pass.

## Pass/fail record

The representative stack passes this mechanical/continuity EVT only if:

- all four gaps meet the provisional target and spread above;
- M2 hardware fits without forced alignment or board deformation;
- J4 housings do not contact and no pin/pass-through damage is visible;
- all 40 expected connections have corrected resistance <= 1.0 ohm at initial,
  bounded-pressure, and post-remate stages;
- every distinct-net adjacent pair is > 50 ohm after 2 s stabilization at the
  pre-mate baseline and all three assembled stages, with no sustained <= 50 ohm;
- C45 residual clearance is at least 0.5 mm; and
- required cable, card and FPC access is usable.

Attach board-revision photos, four gap readings, hardware dimensions, continuity
worksheet, clearance photos and observed failures. A failed item holds assembly
and must not be corrected by bending pins, enlarging holes or omitting J4/C45.

## Remaining release boundary

Passing this plan supports the selected 9.5 mm/M2 representative stack and may
serve as representative J4 assembly evidence. The physical EVT boundary remains
explicit: `fabrication_ready=false`. Production release still requires
resolution of the remaining project blockers in `docs/PROJECT_STATUS.md`,
including J4 land/stencil evidence, missing 3D bodies, runtime pinmux, power,
audio, thermal, cable/enclosure and antenna validation.
