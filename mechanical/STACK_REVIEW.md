# Connector / spacer stack review — conditional, not an assembly release

## Decision

Keep the existing single-board HAT and exact J4. **Do not adopt 4.0 mm or
6.2 mm PCB-surface gaps.** Use the official Radxa standard 2x20 header geometry as the
EVT design basis and target a controlled **9.5 mm PCB-surface gap with M2
fasteners**. This authorizes a representative mechanical/continuity prototype,
not production release; `fabrication_ready=false` until the measured acceptance
checks below pass.

The user supplied the [official ZERO 3W product page](https://radxa.com/products/zeros/zero3w/).
It explicitly offers both 40-pin-header and headerless versions, while Radxa's
hardware-interface documentation describes the 40-pin header as compatible
with most SBC accessories. For this EVT, buy the header-populated version and
treat the official STEP's nominal 2x20 geometry as sufficient; an exact factory
header MPN is not a blocker. Do not desolder a factory header or assume a
headerless purchase.

The known 4 mm CAD case has substantial housing interference. At 6.2 mm the
nominal housing margin is smaller than the socket's drawing tolerance alone.
Larger gaps trade increased underside clearance for reduced pin insertion;
there is no demonstrated universally acceptable stack from pitch alone.

No hardware geometry, connector population, PCB thickness, routing, power
architecture or existing release package was changed by this review. Earlier
uncommitted pinmux documentation remains intact.

## Exact supplier evidence

### Socket: REF-182665-01

- [Toby drawing 1540.pdf](https://www.toby.co.uk/storage/documents/1540.pdf),
  **PDF page 1**, was downloaded and visually inspected. The remaining pages
  describe other part variants and are not a -01 land-pattern approval.
- PDF SHA-256:
  `da639d6c3dbdc5b4d7291ad17144ef28161629ff30bafe24f11771f7b44702fd`.
- Exact drawing height is .144 inch [3.66 mm], not the family web page's
  generic 3.51 mm profile description. General .XXX inch tolerance is
  +/- .005 inch [approximately 0.13 mm]. Confirm its applicability and
  solder seating with the supplier; this is not a complete assembly budget.
- The exact licensed CAD has 3.6576 mm lead-seat-to-housing height. The native
  KiCad export adds a 0.035 mm seat-to-bottom-mask datum offset in this model.
  Do not confuse this export offset with measured solder thickness.

### Supplier-named mating candidate: Valcon THD-20-R

The [REF family product page](https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets)
explicitly names **THD-20-R** as a mating GPIO header. This is materially
stronger evidence than choosing an arbitrary 2.54 mm header, but it does
not identify the factory Radxa header or approve this B.Cu-mounted stack.

[THD drawing 1673.pdf](https://www.toby.co.uk/storage/documents/1673.pdf),
one page, was downloaded and visually inspected. SHA-256:
`2ffcec53adbda15930b3aa25096d2a1139593ee839e71223098653f089a6cdf2`.

| THD-20-R property | Published drawing / specification |
|---|---|
| Contact layout | 20 positions per row, 2 rows, 2.54 mm pitch/cross pitch |
| Post above insulator | 6.1 mm |
| Insulator height | 2.50 mm |
| Solder tail | 3.0 mm |
| Square pin | 0.64 +/-0.02 mm |
| General decimal tolerances | .X +/-0.30 mm; .XX +/-0.20 mm; other rows blank |
| Contacts / insulation | Gold-flash brass / 30% glass-filled PBT |
| Operating temperature | -40 to +105 C |

THD nominal tip height is 8.6 mm above the board before assembly effects;
the existing official Radxa STEP tip is 8.5 mm. **Do not silently substitute
THD dimensions into that STEP or list THD as the installed Radxa part.**
Socket-family 4.1 A/two-powered-pins marketing and male-header 3 A rating do
not qualify the assembled HAT or enlarge its AP63205 2 A envelope.

### Insertion data is published, but its application needs confirmation

The family page says:

> Insertion Depth: (1.78mm) .070" to (3.43mm) .135", pass-through or
> (2.59mm) .102" min plus board thickness for bottom entry

It also calls the family "surface mount bottom entry pass through type".
Toby's [HAT application article](https://www.toby.co.uk/news/latest-news/tobys-top-hat-specification-interconnection-solutions-)
specifically describes soldering REF-182665-01 on the **top** of a HAT, with
the male entering through the HAT PCB. The present board instead has J4 on
B.Cu, with the male approaching the exposed housing face: **top-entry relative
to the connector**, even though the socket is underneath the HAT. Do not apply
the "bottom entry plus board thickness" rule just because its footprint layer
is B.Cu. The related [Samtec HLE catalog](https://suddendocs.samtec.com/catalog_english/hle.pdf)
corroborates the separate entry options and insertion text, but is not an
approval of this custom -01 part/stack. No connector layer was changed.

This is **not** an unambiguous dimensioned -01 section identifying the entry
plane, maximum pass-through travel, contact wipe, and applicable direction
for this socket mounted on the HAT underside. Therefore:

- Record the published values; do not claim no insertion information exists.
- Do not call the axial distance from the lowest socket-model face to the
  male tip an approved insertion depth or contact wipe.
- Do not approve 6.5/7/8 mm merely because the bodies clear, or choose a taller
  spacer by applying the family bounds to an unconfirmed datum.
- Supplier confirmation of the exact case and allowable overtravel remains a
  production-qualification item. It does not block the selected 9.5 mm
  representative EVT, which must directly verify fit and continuity.

## Executed eight-gap CAD sweep

`sweep_stack.py` was exercised against the existing source-bound native STEP
exports with CadQuery 2.6.1. `stack_sweep_9p5_evt.json` contains all eight cases, source
hashes, measured planes, 40 pin-tip faces, and exact BRep distance/intersection
results. At the initial implementation checkpoint, the parent independently
rechecked every bound file hash and reran the opt-in real-CAD integration:
**8 tests passed, no skips** (330.108 s).
The existing mechanical evidence suite also passed **18 tests**; native-export
evidence verification and `git diff --check` passed. These passes establish
analysis execution/provenance, not connector or assembly approval.

Pre-commit follow-up corrected a POSIX publication race: complete temporary
output is now published with atomic exclusive hard-link creation, never a
potentially overwriting rename. Windows and Linux pure suites each passed
**12 tests, 1 opt-in CAD test skipped**; the suite is now included in CI.
The final code separately completed the real gap CAD CLI again, and its
new snapshot reproduced every prior gap result exactly. All bound local-file
hashes were rechecked before replacing the generated snapshot. Independent
code re-review found no blocking errors. Script checkouts are LF-pinned;
metadata raw hashes remain historical local-run provenance as described in
`README.md`, not a platform-independent checkout manifest.

Here `gap` means HAT bottom mask to host board top, **not a purchased spacer
length**. Body clearance is the axial socket-lower-face minus host-plastic-top
plane separation; axial entry is male tip minus socket lower face. Negative
body clearance means overlapping height envelopes.

| Gap mm | Body clearance mm | Axial entry mm | Represented underside min distance mm | C45 maximum envelope distance mm |
|---:|---:|---:|---:|---:|
| 4.0 | -2.1926 | 8.1926 | 0.0050 | 0.4650 |
| 6.2 | 0.0074 | 5.9926 | 2.2050 | 2.6650 |
| 6.5 | 0.3074 | 5.6926 | 2.5050 | 2.9650 |
| 7.0 | 0.8074 | 5.1926 | 2.6550 | 3.4650 |
| 8.0 | 1.8074 | 4.1926 | 2.6550 | 4.4650 |
| 9.0 | 2.8074 | 3.1926 | 2.6736 | 5.4650 |
| 9.5 | 3.3074 | 2.6926 | 2.7773 | 5.9650 |
| 10.0 | 3.8074 | 2.1926 | 2.9628 | 6.4650 |

The underside distance covers **65 represented populated underside components**,
excluding separately analyzed J4 and missing Y1. It can be limited by the host
male pins rather than a vertically adjacent USB-C body; therefore it does not
increase linearly at every gap. All eight represented underside/substrate
intersection volumes are zero; the 4 mm C7 distance is nevertheless unusably
small as assembly assurance.

At 4 mm the low-header-region J4 intersection is **478.029760 mm³**;
at every higher gap that diagnostic regional volume is zero. Complete J4/host
intersection is **498.317310 mm³** at 4 mm, **48.506380 mm³** at 6.2/6.5/7/8 mm,
**43.716407 mm³** at 9 mm, **35.266407 mm³** at 9.5 mm, and **26.816407 mm³**
at 10 mm. It includes modeled
pin/contact geometry and is not automatically classified as either permitted
contact deflection or a rigid collision. No new geometry was substituted to
make it disappear.

**6.2 mm is rejected as a robust candidate:** its nominal 0.0074 mm plane gap is
less than the J4 body-height tolerance alone (0.127 mm). **6.5/7/8 mm are not
approved by housing separation:** their axial entry exceeds the published
1.78–3.43 mm top-entry range if that range applies to this exact custom part.
The 9/9.5/10 mm cases fall numerically inside that range. By user direction,
**9.5 mm is the nominal EVT target** because its 2.6926 mm axial entry is near
the middle of the published 1.78–3.43 mm range and its nominal body clearance
is 3.3074 mm. This does not establish production tolerance or contact wipe;
the representative prototype must prove those physically. At these gaps the
pin tips lie below the HAT PCB, which is not itself a failed connection for a
socket projecting below the PCB.

Measured host pin-tip faces are 0.25 mm squares at Z=8.5 mm; these are tip faces,
**not** shaft-size measurements and not a contradiction of the THD 0.64 mm
nominal shaft. The model cannot identify the physical header MPN.

## Mounting-hole fit: another independent gate

At exact 40-pin alignment, source-bound CAD shows these nearest mount-axis
offsets. HAT nominal holes are 2.7 mm; reference host CAD holes are 2.8 mm.
See [mount_fit_review.json](mount_fit_review.json) for source hashes and math.

| HAT hole center in PCB coordinates, mm | Axis offset, mm |
|---|---:|
| 132.3925, 79.645 | 0.175886 |
| 74.3925, 79.645 | 0.269105 |
| 132.3925, 102.645 | 0.083387 |
| 74.3925, 102.645 | 0.126168 |

For two ideal parallel circular bores and an independently floating straight
shaft, the maximum allowable axis offset is
`(D_hat - d_shaft)/2 + (D_host - d_shaft)/2`.

- A nominal 2.5 mm shaft has only 0.25 mm combined radial budget: one reference
  position exceeds it by 0.019105 mm. Thus the model does **not** support a
  blanket M2.5 screw-fit claim at exact header alignment.
- A nominal 2.0 mm shaft has 0.75 mm combined budget and positive ideal margin
  at every position. **Use M2 hardware for the 9.5 mm EVT stack; this is not yet
  a production-approved spacer assembly.** Thread crests, tolerance, tilt, head/washer/OD,
  board bearing surfaces and neighboring components remain unqualified.
- The official STEP hole centers may be approximate. Do not drill/slot the
  HAT or alter its alignment solely to fit this CAD. Confirm exact-revision
  drawings and real parts first; never tighten screws to bend boards into fit.

A spacer must control surface-to-surface separation, not connector friction.
Its insulating material, OD/ID, actual length tolerance, compression/creep,
flatness and tightening limits matter. A catalog listing with the right
length alone is not enough to nominate an orderable assembly. No spacer MPN
has been added to purchasing outputs. The EVT assembly must
measure and record the actual PCB-surface gap; any washers inside the stack
contribute to that controlled 9.5 mm target.

## Approval handoff

[STACK_APPROVAL_REQUEST.md](STACK_APPROVAL_REQUEST.md) is a prepared,
**unsent** supplier/assembler inquiry retained for production qualification of
the socket insertion window and candidate land/stencil. Exact factory Radxa
header identity is no longer an EVT prerequisite. No supplier was contacted
and no purchase was made.

| Gate | Current disposition |
|---|---|
| Exact J4 nominal geometry / supplier drawing | Digitally established within model scope |
| 4 mm stack | Digitally rejected |
| 6.2 mm gap | Not tolerance-safe from available evidence; not adopted |
| Standard Radxa 2x20 header geometry | Accepted as EVT design basis from official docs/STEP |
| 9.5 mm surface gap with M2 hardware | Selected for representative EVT; physical verification pending |
| Exact mating direction / insertion window / complete tolerance stack | Production approval pending; EVT must record continuity and fit |
| Screw/spacer assembly and exact-revision hole fit | M2 EVT selection; measured fit pending |
| J4 modified land/stencil | External approval / representative assembly pending |
| Missing Y1/top models, cables, FPC, antenna and real component tolerances | Remaining digital/physical mechanical gates |
| Electrical, audio, thermal and OS behavior | Separate physical/runtime EVT pending |

The new eight-gap real CAD CLI completed successfully with all 19 bound files
unchanged through publication. At 9.5 mm, represented underside, C45, maximum
C45 envelope and substrate intersections are all zero; the complete J4 value
above remains the expected pin/contact-solid overlap, while the low rigid-body
header-region intersection is zero. The current pure suite passes 14 tests with
the opt-in real-CAD case skipped; the real CLI result is the published JSON.

Licensed STEP files and supplier drawing rasterizations remain in local
scratch; this report links the original sources rather than redistributing
standalone licensed CAD.
