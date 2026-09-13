# Stage 2 — battery presence and default-OFF amplifier

## Scope and status

The integrated Stage 2 design closes the earlier candidate's three unconnected
items and fourteen physical DRC warnings. It preserves Stage 1 Q2/R8/C39,
the single 65.00 × 30.90 mm four-layer board, connector locations, the AP63205
2 A architecture and all four Qwiic ports. This is digital closure, **not
fabrication or hardware qualification**. No commit, push or production-order
package is authorized by this document.

The earlier `docs/12_CORRECTIVE_REVIEW.md` candidate section is historical.
Never substitute the old GPIO-only temporary candidate for this integrated
source: it predates the Stage 1 power correction.

## Implemented circuit

### Battery presence — J4.31 / GPIO3_B4

- R24 is 100 kΩ from +BATT to Q3 base, with R42 100 kΩ base-to-GND.
- Q3 is Nexperia BC847B,215: 1=B, 2=E, 3=C; emitter goes to GND.
- Q3 collector connects to J4.31 and retained C44. R43 10 kΩ pulls the collector
  to the **host 3.3 V rail**, not the battery.
- Battery connected means **LOW**; with host power alive and battery absent,
  the input is pulled HIGH. This is not an ADC or calibrated undervoltage alarm.
- D2 is removed with its sensing/protection role replaced, not discarded as DNP.
- Powered-off GPIO leakage and startup transients remain physical tests; this is
  not galvanic isolation and no zero-leakage claim is made.

### Amplifier — J4.11 / GPIO3_A1

- J4.11 is now active-high `AMP_ENABLE`, replacing its former NC status.
- R46 100 kΩ pulls Q5 base LOW when the host signal is high-impedance; R45 10 kΩ
  limits base current from the host.
- R44 10 kΩ from +5 V biases Q4 ON while Q5 is OFF, clamping PAM8406 SHDN LOW.
- Driving AMP_ENABLE HIGH turns Q5 ON, pulling Q4 base LOW and releasing SHDN;
  R3, now 10 kΩ, pulls SHDN HIGH.
- Q4/Q5 are BC847B,215. R4 remains the existing 0 Ω MUTE-high link. The new
  hardware controls **shutdown**, rather than claiming codec volume alone
  guarantees a quiet power-on.
- The opt-in `radxa-zero3w-robot-hat-amp.dts` uses the Linux simple-amplifier
  driver and DAPM. It is not automatically installed and requires the corrected
  assembled board, compatible kernel and existing codec overlay.

## Layout and preservation

The final route uses local pad escapes/internal-layer connections, plus a GND
stitch at (104.85, 93.0) mm for the actual isolated copper island. Duplicate
GND vias and a dangling GPIO branch were removed. Four existing visible silk
labels were adjusted; original footprint and connector locations were not moved.

Stage 1 Q2/R8/C39 footprint blocks remain exact. The J4 footprint differs only
by pin 11's new net and a non-electrical native default flag; all other pad nets,
all pad/hole geometry and orientation are unchanged. Stackup, outline, rule
severities, ignored-check lists and original local power geometry remain pinned.

New schematic parts and labels were moved out of the title block and separated
for readability. Native netlist comparison proved every electrical pin/net tuple
unchanged by that drawing-only cleanup; ERC returned to the inherited baseline.

## Verified digital results

- KiCad 10.0.6: **0 physical DRC violations, 0 unconnected items**.
- ERC: **0 errors, 46 inherited library warnings**; no new electrical findings.
- Schematic–PCB parity: **105 inherited Datasheet warnings**. D2/R24/R3 account
  for the three additional resolved warning identities since Stage 1.
- Native XML: **134 components, 98 nets**. PCB: **133 footprints, 1,396 tracks/vias**.
- Exact topology/identity/population/pin-11 guards and deliberate mutation tests
  reject raw-battery reconnection, tied-enabled audio, wrong GPIO/parts, DNP or
  missing safety parts, duplicate records and unrelated upstream pin drift.
- Existing strict-port negative, Qwiic and artwork checks are retained.
- Real native export probe: **130 / 121 full / populated BOM rows**, **133 / 124
  full / populated position rows**, **150 PTH / 42 NPTH**.
- The position CSVs now include all twelve connectors, including J3/J11/J13/J14
  previously excluded by `--smd-only`. They also contain test points/fiducials;
  they are **complete board-position inventories, not an SMT machine feed**.
  The assembler must derive the actual SMT/THT processes from BOM/footprints.
- Two native exports of all **24** files compare byte-identically after the
  existing metadata normalization. This probe is not the full clean-commit
  release manifest/archive integration test; that release test remains unrun.

Evidence: `validation/strict_port/stage2_guard_qualification.json`,
`stage2_native_export_probe.json`, `stage2_export_repro_probe.json`, and the
current canonical ERC/DRC/netlist/report summary. The existing opt-in overlay
compile/apply test uses a synthetic base, not a running Radxa.

## Still required before fabrication approval

1. Exact NP-F550-style pack SKU, polarity, full-charge voltage and cutoff;
   6.0–8.4 V is a design assumption, not verified BMS behavior.
2. Scope GPIO31 leakage/voltage with host power absent and during sequencing.
3. Scope AMP_ENABLE and SHDN through power-on, failed/successful codec startup,
   playback/stop, suspend and shutdown. Bootloader GPIO ownership and pop/noise
   performance are not established by a netlist or DAPM fixture.
4. Stage 1 VS/VGS, R8 hot-plug pulse, Q2 inrush/SOA/thermal and 2 A load tests;
   8 Ω speakers and a measured audio limit remain mandatory.
5. Exact J1/J2/J9/J4 models, J4 land/stencil approval, C45 stack clearance,
   cable/enclosure/RF checks and intended-image Qwiic/UART/I2S validation.
6. USB-C and HAT battery power remain mutually exclusive. No safe source-removal
   or simultaneous-source claim is added.

**fabrication_ready=false. Historical manufacturing packages do not contain
these changes and must not be reused for the Stage 2 assembly.**
