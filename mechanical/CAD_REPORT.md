# Actual Radxa / HAT CAD analysis — conditional reference, NOT assembly approval

## Outcome

**The requested 4.0 mm gap does not describe a mechanically acceptable stack with the male header in the official Radxa STEP and J4 on B.Cu.** Exact J4 restoration is now geometrically established, but the connector bodies substantially intersect. C45 is not the tightest available bottom-side model: **C7 has only 0.005 mm CAD separation from a host USB-C body**. These are digital results, not physical measurements.

Final tested PCB SHA-256: `10decd01363cee7c002294a6e6b6dbfa8d8b9488eec4e8337256af82ff02f592`, on HEAD `9ae7252f5ffe37efb9ec986b2e93972cd3280f16` with the parent's uncommitted, model-only J4 restoration. The first analysis used PCB SHA `67ec3446de5e63c03ef6e9326a7a828437cfa5d92d7d0d3dd3b0bee7026e4771`; **all final CAD checks were rerun using fresh native exports from the final source**. `cad_evidence.json` confirms source SHA unchanged during that final analysis. This worker made no existing PCB, library, checker or documentation edits.

## Methods and coordinate datums

KiCad 10.0.6 native STEP exports, CadQuery 2.6.1 / OCP 7.8.1.1.post1, real BRepExtrema minimum distances and solid Boolean intersections were exercised. Distances below are measured **in CAD**. No physical spacing, solder height, insertion depth or contact force was measured.

Official STEP units import as millimetres, corroborated by 2.54 mm header pitch and board dimensions. The official host's large planar board faces have plane origins Z=0 and Z=-1.6 mm; apparent bounding-box excursions of up to roughly 0.006 mm on those faces are imported model tolerances, not another board thickness. Host header plastic top is Z=2.5; pin tips are Z=8.5. Board-plane XY bounds are approximately X=-0.013470…65.001648, Y=0…30.005528. **The complete host assembly**, including projecting connectors, is larger: X=-0.013470…65.001648, Y=-1.500000…30.005528, Z=-4.484104…8.500000 mm. The previous document's approximately 65×30 envelope must not be called the entire assembly envelope.

Native KiCad STEP was exported with `--user-origin 0x0mm`: X equals PCB X and Y equals negative PCB Y. HAT substrate is Z=0…0.84; a separate native pads+mask export establishes bottom/top mask planes at -0.085/+0.925. The PCB declares 1.0 mm total thickness; the exported mask-to-mask 1.010 mm envelope includes native modelling offsets and is **not a physical thickness specification**. Native C45 and J4 lead seating is Z=-0.12. Treating substrate Z=0 as the external mating surface would introduce an avoidable datum error.

The 4.0 mm comparison places the exported HAT bottom mask at host Z=4.0, so native STEP Z translation is **+4.085 mm**. This native export convention leaves a 0.035 mm seating offset beyond that mask plane; it is not a measured solder thickness.

## XY alignment: the old transform is only approximate

Both placements were tested:

| Placement | Native HAT STEP → official Radxa STEP translation, mm |
|---|---|
| Previously documented nominal | `(-70.9025, 106.135, 4.085)` |
| Actual 40-pin header-grid alignment | `(-70.947472, 106.31508, 4.085)` |

No 3D rotation is needed between these STEP coordinate frames. For PCB editor coordinates the second transform is `Xr=Xhat-70.947472; Yr=106.31508-Yhat`. To place the actual host into **unshifted native HAT STEP** for a renderer use the inverse translation `(70.947472,-106.31508,-4.085)`. These translations are **not** KiCad footprint-model-local offsets.

The second transform is derived from all 40 official host pin-tip faces and the 40 actual J4 NPTH passages. It eliminates their 0.185611 mm XY residual under the old nominal transform. However, **it does not simultaneously make the mounting holes exact**:

- Actual HAT MP holes: `(132.3925,79.645)`, `(74.3925,79.645)`, `(132.3925,102.645)`, `(74.3925,102.645)`; diameter 2.7 mm. The prior document's centers differ by about 0.01 mm.
- Official STEP mount axes: `(3.549904,3.599942)`, `(3.599942,26.450036)`, `(61.399928,26.500074)`, `(61.399928,3.599942)`; diameter 2.8 mm.
- Nearest mount-axis residuals, in the HAT order above, are 0.175886, 0.269105, 0.083387, 0.126168 mm at header-grid alignment; 0.090634, 0.116980, 0.142127, 0.125203 mm at nominal alignment.

Thus the STEP's hole rectangle is not an exact 58×23 rectangle. Do not assert exact four-hole alignment or screw fit from this file. Compare the exact physical host revision, DXF and measured parts before fixing spacer locations. Electrical pin-1 confirmation requires the separate schematic/header evidence; unlabeled geometric pin tips alone do not prove pin numbering.

Native substrate-to-host analysis gives **0.772831 mm³ intersection under the old transform**, at displaced host pins passing through the HAT. Header-grid alignment removes that intersection and gives **0.050381 mm** minimum substrate/pin separation. This tiny radial model margin is not a drill-tolerance signoff.

## Exact J4 restoration and stack collision

See [J4_PLACEMENT.md](J4_PLACEMENT.md) for the proven current model block. Native final-source readback contains only `${KIPRJMOD}/models-local/REF-182665-01.step`, offset `(0,-4.19905533063427,0.302503373819)`, rotation `(-90,0,90)`, scale `(1,1,1)`. Neither the Raspberry Pi assembly nor the unrelated FH-00339 connector is used as mechanical evidence.

Both peg axes match actual PCB centers `(80.5375,79.64)` and `(126.2575,79.64)` within 0.000001 mm in native export. Exact-model peg diameter is 1.5875 mm; pitch 45.72. Length 50.8, lead span 6.5786, lead-seat-to-body-top height 3.6576 mm agree with the nominal 50.8 / 6.58 / 3.66 supplier dimensions. All 40 lead seating faces are at native Z=-0.12. Their centers are offset 0.226730 mm from their nearest outward SMD pad centers in the row direction; this reflects lead/pad length differences, not a peg-grid displacement. It is not approval of paste coverage or solder joints. J4 solid vs HAT substrate has zero intersection and 0.12 mm minimum separation; its pegs pass through the intended holes.

| Assumed surface gap | Exact J4 ∩ complete host, mm³ | Intersection within header footprint below Z=2.499, mm³ |
|---|---:|---:|
| 4.0 mm | 498.317310 | 478.029760 |
| 6.2 mm | 48.506380 | 0 |
| 6.5 mm | 48.506380 | 0 |

At 4 mm the socket's lowest face is host Z=0.3074, far below the male plastic top at Z=2.5. The large low-height overlap demonstrates **body interference**, not ordinary spring contact. The diagnostic header-region window is merely a Boolean selection volume, not an approximate connector replacement.

At 6.2/6.5 mm the low-height body interference disappears, but complete solids still overlap at pin/contact regions. **Neither spacing is approved here.** Resolve exact male-header MPN and length, pin insertion limits, intended body orientation and spring contact geometry with the supplier, then repeat the model and physical checks. The official STEP's included header is not proof that the intended physical SKU is populated with that exact header.

## C45 and the broader underside

The current generic KiCad 1210 model is **2.5×3.2×2.5 mm in its placed axes**, not an erroneously short model. It matches the exact C45 nominal package dimensions. The Murata part-specific sheet explicitly covering GRM32ER71H106KA12L specifies length 3.2±0.3, width 2.5±0.2, **thickness 2.5±0.2 mm**. Therefore the generic model omits maximum-material and process tolerances.

At 4 mm surface gap:
- Nominal C45-to-host CAD distance: **0.665 mm**, zero intersection. Nearest host face Z=0.8 lies in the central package region identified as U1/RK3566 by the separate placement evidence.
- A separately labeled **maximum-dimensional MLCC bounding envelope**, 2.7×3.5×2.7 mm at the same seating plane, gives **0.465 mm** CAD distance, zero intersection. This is a conservative envelope, not an exact supplier STEP replacement. It is already below the 0.5 mm residual gate before solder, board bow and tolerance variation.
- Nominal C45 gap sensitivity: 3.5 / 3.84 / 4.0 / 4.5 mm surface gaps produce 0.165 / 0.505 / 0.665 / 1.165 mm CAD separation respectively. These are not approved spacer prescriptions.

The final PCB has 73 B.Cu footprints, 67 populated. Native export excludes J4 for its separate exact analysis and excludes the six DNP references R11/R10/C25/U4/R41/R17. **Y1's model is missing**, leaving 65 represented populated underside components. Native warnings are retained in scratch. No exact WAGO model was fabricated or substituted. Top components, MK1, cables, heatsinks and spacers are outside this collision set.

All represented underside solids have zero host intersection at 4 mm, but small gaps make a blanket pass inappropriate. Header-aligned local CAD distances below 1 mm:

| HAT reference(s) | Minimum distance to host, mm |
|---|---:|
| **C7** | **0.005** |
| C6, C8, C9, FB2, FB3 | 0.305 |
| C37 | 0.412485 |
| R3 | 0.455 |
| C45 | 0.665 |
| U5, U6, U7 | 0.815 |

C7's nearest host point is `(43.950029,3.605079,3.16)` on a USB-C body. C7 is only 5 micrometres above that model face. CAD zero intersection with such a tiny nominal gap is **not physically meaningful clearance approval**. The above distances use full-solid global minimum-distance/intersection checks, then conservative 1 mm face bounding-box filtering for individual component proximity. Components are identified by native model center matching actual PCB placement.

## Evidence, source hashes and reproduction

- [cad_evidence.json](cad_evidence.json): final-source datums, model bounds/hashes, 40 pin centers, four mounting axes, both transforms, exact distance witness points, intersections and C45 sensitivity.
- [j4_evidence.json](j4_evidence.json): actual final-source J4 export, 40 lead faces, peg verification and three-gap Boolean results.
- [stack_4mm.png](stack_4mm.png), [stack_4mm_header_side.png](stack_4mm_header_side.png): exercised, visually inspected VTK renders of actual tessellated CAD in the integrated stack. HAT substrate is translucent blue, official host green, exact J4 orange, C45 red. These are deliberately **partial** assemblies and label the collision; the side view crops board ends to emphasize the header.
- [render_evidence.json](render_evidence.json): actual input STEP hashes and tessellation counts.
- [README.md](README.md): exact runnable commands and environment notes.

Official STEP ZIP source: https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_3d_stp.zip

ZIP SHA256 `0dfc39db5f52665ef92bcab34781132aba399a4061dc2c869f757a00f446d2cf`; extracted STEP SHA256 `1eac96aa8804f7270e08610ebd99bf0eccfd26d39d859fae76d119406694ded3`. Fresh retrieval matches the pre-existing cache exactly.

Exact J4 licensed asset SHA256 `d5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5`, acquired by the parent from the linked public Samtec/SnapEDA asset. Supplier dimensional drawing: https://www.toby.co.uk/storage/documents/1540.pdf . Raw licensed part and STEP stack exports are kept only in scratch/local licensed storage, not redistributed here.

C45 part-specific Murata sheet, third-party mirror: https://datasheets.b-cdn.net/files/GRM32ER71H106KA12L-Murata-datasheet-12553172.pdf ; downloaded PDF SHA256 `59b89eed344603cf4778bebb61ba60f887e3a33a8fd5f433c4651b25353f9100`. Sheet page 1 covers L/K/B packing suffixes and is dated 2012/11/10; it cautions that detailed ordering/approval specifications must be confirmed. Thickness max 2.70 mm independently appears at https://www.digikey.com/en/products/detail/murata-electronics/GRM32ER71H106KA12L/2548481 . Generic installed KiCad `C_1210_3225Metric.step` SHA256 `f8510481c5044113cf49b0fa6dd54ddab9224508bd6808e1afab8ef0cefdefc9`.

**Gate disposition:** actual Radxa reference and exact J4 geometric restoration are digitally established; 4 mm stack clearance is digitally rejected for these models; exact connector stack, land/paste approval, mounting fit, real solder/height tolerances, cable/enclosure access and physical first article remain open. RF, loads, temperature and firmware were not evaluated by this CAD task. **Fabrication-ready: no.**
