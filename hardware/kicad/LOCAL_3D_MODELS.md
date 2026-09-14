# Local 3D model provenance

Individual supplier/CAD-provider models are **not automatically redistributable**.
`models-local/` is ignored by Git. Keep each provider's license with its model.
A fresh clone does not contain these files; do not treat its partial render as a
complete assembly. No approximate replacement is authorized by this document.

## J4 — exact REF-182665-01

- Purchasing identity: Toby Electronics REF-182665-01; manufacturer drawing: Samtec REF-182665-01.
- Product: https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets/REF-182665-01
- Drawing: https://www.toby.co.uk/storage/documents/1540.pdf — **page 1** is the exact `-01`; other pages describe different parts.
- Samtec public item lookup: https://www.samtec.com/api/itemmaster/productseriesoption/ref-182665-01 — identifies exact part, partId 8771510.
- Samtec public CAD availability: https://www.samtec.com/techspecs/blocks/aremodelsavailable/ref-182665-01 — returned true.
- Manufacturer-linked CAD embed: https://www.snapeda.com/parts/REF-182665-01/Samtec%20Inc./embed/?ref=samtec
- Published public STEP download endpoint: https://www.snapeda.com/parts/snapapi/download-component-public/10288326/4783345/step/?ref=samtec&user_email=
  This is the endpoint called by the embed's `get3dDownloadUrl` in `/static/js/3dViewer.js`; the public blank-email fallback returned a ZIP download URL. No login, guessed credential or account was used. Temporary signed download URLs are deliberately not recorded here.
- ZIP model member: `REF-182665-01--3DModel-STEP-484052.STEP`.
- Local target: `models-local/REF-182665-01.step`.
- SHA-256: `d5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5`.
- STEP header: `REF-182665-01.step`, AP203, SolidWorks 2016, dated 2018-02-26. Preserve original bytes.
- ZIP also includes `License.txt`; stored locally as `models-local/J4-License.txt`.
- License permits design/manufacture/distribution of combined circuit designs but restricts distribution of individual models. Do not commit or distribute the standalone STEP. Re-acquire from the provider for another workstation and review the then-current license.

### Exact drawing comparison

Native PCB extraction against supplier page 1 establishes:

| Feature | Exact drawing | Active PCB |
|---|---|---|
| Electrical pitch | 2.54 mm | 2.54 mm passage grid |
| End contact-center span | 48.26 mm | 48.26 mm |
| Locator pitch | 45.72 mm | 45.72 mm |
| Locator diameter / hole | nominal 1.588 mm peg | 2.00 mm NPTH |
| Pin passages | 2 rows of 20 | 40 holes, diameter 1.02 mm |

The locator's nominal diametral difference is 0.412 mm; this is not a tolerance
stack or an assembler-approved fit. The exact drawing labels height 3.66 mm;
do not substitute the series marketing description's 3.51 mm for exact CAD
qualification. The drawing does **not** provide the exact recommended land or
stencil pattern. The modified 1.02 x 1.80 mm lands remain externally unapproved.

## WAGO — J1/J2/J9

Exact MPN: `2059-302/998-403`.

- Official product: https://www.wago.com/global/pcb-terminal-blocks-and-pluggable-connectors/smd-pcb-terminal-block/p/2059-302_998-403
- Downloads API: https://www.wago.com/wagoapi/v2/global-wago/products/2059-302_998-403/downloads?lang=en_GG
- Official MCAD submodel: https://c1.api.wago.com/smartdata-aas-env/submodels/aHR0cHM6Ly93YWdvLmNvbS9pZHMvc3VibW9kZWwvMjA1OS0zMDIvOTk4LTQwMy9NQ0FE
- It identifies WAGO, exact MPN, STEP AP214 and the file URL:
  https://c1.api.wago.com/smartdata-aas-generator/api/v1/download/cad/2059-302%2f998-403.stp
- That published file URL returned HTTP 404 during this review. The metadata
  record is not a downloaded STEP. An empty HTTP response must not be installed.
- Manufacturer-specified dimensions are 5.9 mm wide, 7.9 mm deep, 2.7 mm high,
  3 mm electrical pitch. These are supplier values, not measured CAD dimensions.

## Render completeness limits

The initial native inventory is in `validation/mechanical/model_inventory.json`.
The initial review also found unresolved MK1 and Y1 model references. MK1 is
LinkMems `LMA2718T421-OA5-2`; Y1's purchasing MPN includes leading whitespace in
the original source (`    OT3EL89CJI-111YLC-12M`, YXC). Its referenced Abracon
model is not present in the installed library and is not exact YXC identity.
These are additional model-qualification gaps, not permission to change the
BOM, pinout or populated state. U4 is DNP; fiducials intentionally lack bodies.

`fabrication_ready=false`. CAD geometry, resolved paths and completed renders
are not measurements of physical connector seating, bow, solder or RF behavior.
