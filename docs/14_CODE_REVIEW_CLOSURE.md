# Pre-commit review and finding validation

## Scope

Review covers the staged CI/library setup repair, exact Ubuntu export metadata
normalization, J4 model-only restoration, and new mechanical evidence scripts.
It does not approve PCB fabrication, change the single-board architecture, or
include restricted standalone STEP assets / historical production releases.

Two independent read-only reviewers inspected the staged changes. The parent
then ran the reported negative cases in temporary copies, not against published
evidence. The CI/export/guard/model-policy reviewer found no blocking defect.
The CAD reviewer independently recomputed C45 separation and J4/host intersection
from the final native STEP files and agreed with the recorded numerical results.

## Validated findings

| Finding | Parent reproduction on original staged version | Disposition |
|---|---|---|
| Historical cache was an undocumented prerequisite | Removing only optional cache identity from the copied evidence caused exit 1 despite valid fresh inputs | Fixed: actual official ZIP/STEP bytes must match reviewed pins; no-cache replay now passes |
| Empty renderer source inventory passed | `sources=[]` still produced `evidence_complete=true`, exit 0 | Fixed: exact source/output inventory, transform and hash binding; empty/duplicate/missing/unexpected records reject |
| Corrupt PNG passed superficial header checks | Original first 24 bytes plus zero padding still produced success | Fixed: decode/CRC/load integrity plus renderer output hashes; corrupt PNG rejects even with a forged matching recorded hash |
| Optimization disabled verification assertions | `python -O` accepted an incorrect source PCB hash | Fixed: optimized verification is explicitly rejected before acceptance checks |
| CAD analysis export inventory was incomplete | Removing both the `surfaces.step` manifest entry and its file still passed in the first corrected version | Fixed in the second focused cycle: require the exact five CAD exports before other validation; missing/empty/unexpected inventories reject |

Related provenance hardening (exact official-asset pins, bounded download,
current-J4 export binding and renderer output binding) is limited to preventing
these reproducibility/false-acceptance failures, not changing CAD geometry.
Current J4 now has its own source/model/export metadata instead of borrowing
the candidate's provenance. Renderer writes must all decode successfully in a
temporary directory before image replacement; the metadata file is replaced
last. A failed write cannot attach newly recorded inputs to a stale PNG.
Style-only changes and the already disclosed missing WAGO/MK1/Y1 models are not
being used to expand this review into a redesign.

## Baseline and pre-fix tests

- Isolated HEAD `9ae7252f5ffe37efb9ec986b2e93972cd3280f16`: manufacturing
  tests ran 26 cases, with 2 native integration cases skipped; no failures.
- Staged candidate in an isolated clean Git fixture, with
  `RUN_KICAD_INTEGRATION=1`: all 27 manufacturing tests passed, including full
  deterministic export/archive verification. That fixture is not a production
  order package and does not commit the user's working branch.
- Current-source native strict-port checks passed on Windows and Ubuntu/KiCad
  10.0.6; physical DRC and unconnected counts remain zero. Stage 1/2 acceptance,
  mutation/parity/artwork and synthetic amplifier overlay tests passed.
- Clean-clone model policy: two reference checks passed, licensed local model
  hash check explicitly skipped when the restricted file was absent. This is
  not a claim of complete rendering in a fresh clone.
- Added-line security scan found no secret literals, `shell=True`, dangerous
  eval/exec, or pickle deserialization. No ruff/mypy installation was available.

## Final review / publication

- Parent-owned replay against the corrected actual evidence: baseline and
  no-cache cases pass; empty renderer sources, corrupt PNG with matching
  recorded hash, and optimization bypass all fail for the intended diagnostics.
- All 18 offline mechanical regression tests pass in the reproduced Ubuntu
  environment without licensed models or the historical scratch directory.
  They are included in CI, with explicit Pillow installation.
- The exact CI validation command block passed again on the final corrected
  clean staged snapshot, including all 18 mechanical tests, the full 27-case
  native manufacturing suite and merged Qwiic overlay checks. The final
  inventory-only correction was also verified by direct parent replay.
- A later security scan matched this document's sentence mentioning absence of
  unsafe shell invocation. Context inspection classified it as a documentation
  false positive, not executable code; no unresolved security finding remained.
- Exact J4 was freshly exported and analyzed, both images freshly rendered,
  and the final source-bound evidence verified. Numerical CAD findings remain
  unchanged; only provenance and validation behavior were strengthened.
- Independent final re-review passed after the second focused correction,
  with no remaining security or logic findings. The reviewer independently
  passed all 18 tests on Windows and Linux and confirmed the specific missing
  CAD-export rejection without weakening other guards. Only this review record
  was finalized afterward; reviewed source code was not changed.
- User authorized commit/push; no production order is authorized. The published
  commit and its exact GitHub workflow run provide the remote publication/CI
  record rather than a pre-printed success claim in this pre-commit document.
Keep `fabrication_ready=false`: the 4 mm CAD stack is rejected and no replacement
header/spacer assembly is approved.
