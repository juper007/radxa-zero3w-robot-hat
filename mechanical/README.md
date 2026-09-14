# Reproduce the CAD review

Read [CAD_REPORT.md](CAD_REPORT.md) for findings, assumptions and physical limits. Nothing in this directory authorizes fabrication or a 4 mm connector stack. No licensed standalone model is stored here.

## Windows commands (Git Bash)

The following paths are the actual exercised environment. Change `S` for a new scratch run. The installed KiCad CLI and bundled Python are both 10.0.6. `python` for CAD is an isolated uv environment, not KiCad's Python.

```bash
R='C:/Users/juper/OneDrive/Documents/ChatGPT/Microduck_DIY/radxa-zero3w-robot-hat'
K='C:/Users/juper/AppData/Local/Programs/KiCad/10.0'
S='C:/Users/juper/AppData/Local/Temp/radxa-cad-final'
V='C:/Users/juper/AppData/Local/Temp/radxa-cad-venv'
J='C:/Users/juper/AppData/Local/Temp/robot-hat-model-research/REF-182665-01.step'

# Only if creating a new CAD environment:
uv venv "$V" --python 3.11
uv pip install --python "$V/Scripts/python.exe" -r "$R/mechanical/cad-requirements.txt"
# PyPI's files.pythonhosted.org failed TLS handshake in this environment.
# The successful alternative used a public PyPI mirror (not --insecure):
# uv pip install --python "$V/Scripts/python.exe" \
#   -r "$R/mechanical/cad-requirements.txt" \
#   --index-url https://mirrors.aliyun.com/pypi/simple

# Downloads the official Radxa archive and enforces reviewed ZIP/STEP hashes.
# Historical cache comparison is informational; no old cache is required.
# inspects current PCB natively, and exports C45, substrate, masks/pads and
# populated available underside models excluding J4 (reviewed separately).
"$K/bin/python.exe" "$R/mechanical/prepare_inputs.py" --scratch "$S"

# Exports both the scratch candidate and the actual source J4; source stays read-only.
# Current export has dedicated PCB/model/STEP/transform hash binding.
# Requires the legitimately acquired licensed model, with its pinned SHA.
"$K/bin/python.exe" "$R/mechanical/prepare_j4.py" --model "$J" --scratch "$S"

"$V/Scripts/python.exe" "$R/mechanical/analyze_cad.py" --scratch "$S"
"$V/Scripts/python.exe" "$R/mechanical/analyze_j4.py" --scratch "$S"
"$V/Scripts/python.exe" "$R/mechanical/render_stack.py" --scratch "$S"
"$V/Scripts/python.exe" "$R/mechanical/verify_evidence.py" --scratch "$S"
# Offline synthetic regressions, only Python + Pillow needed:
"$V/Scripts/python.exe" "$R/mechanical/test_evidence.py" -v
```

Final native export commands returned 0; final `analyze_cad.py`, `analyze_j4.py` and `render_stack.py` process results returned 0. Both PNGs were opened and visually inspected. The CAD script completed after its full distance/intersection checks and STEP assembly export; `source_unchanged_after_analysis` is true for the final-source run.

Final `verify_evidence.py` also returned 0 and wrote `verification.json`: source binding, all input STEP hashes, 40 header tips, 40 J4 lead faces, both transforms, three J4 gaps, 65 represented underside bodies, 12 close-component identities, and both 1600×1000 PNG files verified. Its result deliberately says `evidence_complete: true` and `fabrication_ready: false`.

## Outputs

Repository `mechanical/` holds scripts, pinned Python dependencies, JSON evidence, Markdown findings, and integrated PNG renders. `analyze_j4.py` requires `j4-current.step` and its dedicated `j4-current-metadata.json` from `prepare_j4.py`; candidate provenance is never substituted. PCB bytes, licensed local model bytes, exact transform and export SHA are checked before analysis and again by the verifier. Re-export after source changes. The render script requires the direct current export.

Final scratch directory `C:/Users/juper/AppData/Local/Temp/radxa-cad-final` contains:

- `official-current.zip`, `official_radxa.stp` — fresh verified official source.
- `inputs.json`, `commands.json`, `*-export.log` — full native input inventory and commands.
- `c45.step`, `board.step`, `surfaces.step`, `bottom.step` — native exports.
- `j4-candidate.kicad_pcb`, `j4-test.step`, `j4-current.step`, `j4-export-metadata.json`, `j4-current-metadata.json` — exact-model placement proof and actual current-source export.
- `partial_stack_header_aligned.step` — official host + substrate + available underside bodies, deliberately excluding J4.
- `LICENSED_partial_stack_J4_4mm.step` — integrated host + substrate + exact J4, showing the interference. Keep this licensed derivative local; do not redistribute the standalone source part.

The prior exploratory run and C45 supplier PDF are at `C:/Users/juper/AppData/Local/Temp/radxa-cad-analysis`. Final evidence was **rerun** from `radxa-cad-final`; it is not just relabeled earlier data. Direct STEP DATA equality was not assumed: native export ordering/presentation and tiny healed-edge coordinates differed, so a failed exploratory byte-equivalence check was retained only in scratch and the final geometry was checked anew.

## Evidence hardening replay

The hardened `prepare_j4.py`, `analyze_j4.py`, `render_stack.py` and full verifier were exercised against `radxa-cad-final`; all returned 0. The source PCB SHA remains `10decd01363cee7c002294a6e6b6dbfa8d8b9488eec4e8337256af82ff02f592`. New dedicated J4 provenance is published by the native exporter, not retroactively attached to an old export. The three-gap J4 intersections are unchanged. The unchanged substrate/underside/C45 exports remain hash-bound to the earlier full CAD analysis.

Verifier and tests now use Pillow (already pinned in `cad-requirements.txt`), not bare system Python without dependencies. Render validation requires exactly five named STEP sources, exact translations, two named PNG outputs, recorded SHA/byte counts, PNG chunk verification and full pixel decoding. VTK writes to fresh temporary paths; both files are decoded and source hashes rechecked before replacing outputs, with metadata committed last. A write failure cannot bind new sources to stale images. These checks establish provenance/integrity, not physical assembly approval. Optimized verifier execution (`-O`/`PYTHONOPTIMIZE`) is explicitly rejected.

`test_evidence.py` uses only synthetic temporary PCB/STEP/ZIP bytes and PNGs plus the public JSON schema. After the second review's exact CAD-export inventory correction, final execution passed **18 tests** on Windows CAD Python and **18 tests** in the parent's Linux Docker environment (`docker exec -w /source strict-ci-linux-34786194068 python3 mechanical/test_evidence.py -v`). Both rerendered PNGs were visually inspected after successful decoding. It needs no KiCad, OCP, network, real local model or historical scratch directory. Test-only asset pin substitution is confined to the isolated synthetic process; the production CLI has no bypass. Inventory, transform, source/output hash, PNG decode, no-cache, optimized execution, failed publication, bounded download and current-J4 binding cases are checked independently with diagnostic assertions. The CAD export manifest must contain exactly `official_radxa.stp`, `c45.step`, `board.step`, `bottom.step`, and `surfaces.step`; deleting even the surface-datum file and its record is rejected.

Official acquisition has a 30-second socket timeout, checked 120-second transfer deadline, 16 MiB archive and 64 MiB extracted STEP limits. It pins both hashes listed in CAD_REPORT before publication. A fresh real HTTPS acquisition through the new code succeeded at `C:/Users/juper/AppData/Local/Temp/radxa-fresh-pinned-_misrv9n`. Previous evidence and scratch were preserved at `C:/Users/juper/AppData/Local/Temp/radxa-evidence-before-fix-64suq43j`.

## Known execution limitations

- The first CadQuery probe printed valid geometry then exited with Windows status 127 during interpreter teardown; this was not reported as a successful completed analysis. Current standalone CAD scripts deliberately flush all required outputs and call `os._exit(0)` **only at the successful end**, avoiding the OCP/VTK teardown issue. Exceptions and incomplete checks do not reach that exit. This is an explicit execution workaround, not concealment of failed CAD operations.
- A guessed mask datum of -0.08 failed an assertion. The analysis now measures the actual mask export (-0.085) and verifies it is in the expected range. Large mask face evidence is stored, so the datum is auditable.
- A slow exploratory per-component/full-fused-host distance loop was stopped and replaced with conservative per-face 1 mm bounding-box filtering. Full-solid aggregate distance and Boolean checks remain in place; bounding boxes alone never substitute for those checks.
- The official model is heavily fused and simplified. The named U1/package interpretation relies on separate placement documentation, not a recovered STEP assembly name. Model tolerance, solder, bow, screws, real cable overmolds, RF and contact mechanics remain separate gates.
- Native bottom export explicitly warns about missing Y1. J4 is now exact and local; missing WAGO bodies/top assembly are not silently replaced.

## Reuse and scope

`prepare_inputs.py` and `prepare_j4.py` only read the real source PCB and write scratch files. The analysis scripts overwrite their own `mechanical/` evidence on a new run. Model licensing/acquisition is a prerequisite; these scripts do not bypass access controls or download a substitute connector. Parent work restored the existing PCB's J4 model; this CAD worker's repository writes are limited to this new `mechanical/` directory. No commit or push was performed.
