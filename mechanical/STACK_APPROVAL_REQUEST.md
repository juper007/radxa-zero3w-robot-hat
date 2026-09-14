# Supplier / assembler clarification — DRAFT, NOT SENT

Subject: REF-182665-01 production insertion window and PCB land approval

We are evaluating an unchanged single-board Robot HAT with a Toby/Samtec
REF-182665-01 socket populated on B.Cu. No purchase or assembly release is
being requested by this draft. Please provide written approval tied to the
exact socket and PCB/stack revision. The official Radxa standard 2x20 header
geometry is already accepted as the representative EVT basis.

## Controlled design facts

- HAT is 1.0 mm nominal PCB, 2x20 at 2.54 mm pitch.
- J4 is B.Cu mounted; locator pegs enter the HAT, socket housing projects
  toward the host. Its exact native-export geometry has been checked against
  the footprint and supplier nominal dimensions.
- J4 candidate lands: 1.02 x 1.80 mm, 40 pin passages 1.02 mm NPTH,
  locator-hole pattern unchanged. The exact drawing does not establish an
  approved land/stencil for this modified candidate.
- Official Radxa reference CAD includes standard 2x20 male-header plastic
  2.5 mm above the host board and pin tips 8.5 mm above it. This geometry is
  accepted for EVT; exact factory header identity is not an EVT prerequisite.
- The earlier 4.0 mm host-top to HAT-bottom surface gap has a demonstrated
  housing collision. A 9.5 mm nominal surface gap with M2 hardware is selected
  for representative EVT. Contact-solid intersection in undeformed STEP models
  is not an insertion/wipe or retention-force test.

## Questions for Toby / Samtec

The REF family page names THD-20-R and publishes this insertion wording:
"(1.78mm) .070\" to (3.43mm) .135\", pass-through or (2.59mm) .102\" min
plus board thickness for bottom entry". Please resolve the applicable case,
datum and overtravel limits for the exact -01 socket in this B.Cu orientation;
we have not treated the family text as a dimensioned mating acceptance window.
THD drawing 1673.pdf gives a 6.1 mm post above a 2.50 mm insulator, 3.0 mm
solder tail and 0.64 +/-0.02 mm square pins. THD is a supplier-named candidate,
not an identification of the factory Radxa header.

1. Confirm the permitted mating direction for this exact -01 part when
   B.Cu-mounted and entered from the housing side facing the host. Identify
   the entry plane and active contact region in a dimensioned section.
2. Specify the qualified male pin cross-section, tip/chamfer, tolerances,
   straightness and plating. Is the proposed male header explicitly qualified
   with this socket, rather than merely sharing 2.54 mm pitch?
3. Give exact recommended male-header series and orderable MPN options,
   including rows/positions, post length above insulator, insulator height,
   PCB solder-tail length, plating and temperature rating. Do not substitute
   a socket purchasing identity for a male header identity.
4. Provide minimum and maximum insertion depth, minimum contact wipe,
   allowed axial float, maximum pin protrusion/pass-through limits and any
   prohibition on housing-to-housing bottoming. State the reference datum
   for each limit. What stack-height interval meets these limits with a
   1.0 mm HAT and the identified male header?
5. Provide connector dimensional tolerances and solder seating assumptions
   needed for the worst-case stack; confirm whether the drawing's general
   .XXX inch tolerance applies to the .144 inch socket height.
6. Review the actual 1.02 x 1.80 mm land and 1.02 mm NPTH passage pattern.
   Supply approved copper, solder-mask and stencil/paste geometry, locator
   tolerances, solder process, coplanarity and inspection acceptance criteria.
7. State mating/unmating force for the completed 40-contact assembly, cycle
   rating and acceptable mechanical retention method. A contact retention
   force note alone is not approval of board extraction loading.
8. Confirm allowable current with the actual simultaneously powered contacts,
   ambient temperature and selected plating. This review does not enlarge the
   existing AP63205 2 A operating envelope.

## Optional production questions for Radxa / host supplier

- Confirm production revision control for the header-populated ZERO 3W.
- If available, provide header tolerances and current rating; this is not a
  prerequisite for the representative EVT build.
- Confirm host mounting-hole diameters and true centers for that revision.
  The reference STEP and HAT holes do not form an exactly coincident set
  when the 40-pin grid is aligned. Do not force screws through mismatched holes.

## Questions for spacer supplier / assembler

- Quote a controlled, insulating M2 spacer solution that produces a measured
  9.5 mm PCB-surface gap, with length tolerance, OD/ID, end-face flatness,
  temperature, compression/creep and tightening-torque limits.
- Include screw/washer/nut dimensions, material, thread engagement and head
  envelopes. Check both boards, all four locations, copper/mask bearing lands
  and neighboring components. Insulating material does not remove crushing,
  creep or alignment concerns.
- Use the named surface-to-surface datum. Added washers/shims inside the
  stack change the gap and must be included in the tolerance calculation.
- Keep connector friction out of the spacing definition. Verify continuity
  and insertion without using screw tension to bend the PCB into engagement.

## First-article records required after digital approval

Record board markings and pin-1 photos; actual male post/insulator height;
spacer lengths; all four assembled gaps; pin protrusion and mating depth;
C45/Radxa clearance (at least 0.5 mm residual under the established project
gate); all underside component clearance including missing Y1 model;
connector solder joints and continuity; accessible cables/FPC/antenna; and
mating force/board deflection. Keep power disconnected during mechanical fit
and continuity checks. Electrical power/thermal/audio/runtime EVT remains
separate. Fabrication-ready remains false until the applicable gates close.

Reference drawing (link only; no licensed model redistribution):
https://www.toby.co.uk/storage/documents/1540.pdf — exact -01 is PDF page 1.

Header drawing: https://www.toby.co.uk/storage/documents/1673.pdf (one page).
Family mating guidance:
https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets
