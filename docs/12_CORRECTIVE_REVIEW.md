# Staged corrective review — not fabrication approval

**Superseded status:** Stage 2 integration closes the GPIO/audio routing blockers
recorded below. Current source/verification and remaining physical gates are in
`13_STAGE2_GPIO_AUDIO_CLOSURE.md`. The old temporary candidate must not replace
the integrated active board. This document retains the earlier review chronology.

## Approved scope

- Keep one PCB, the original outline, AP63205 2 A and every required connector.
- Intended supply: an NP-F550-style lithium-ion camera battery, described by the user as 7.2–7.4 V. This is a nominal pack description, not proof of the exact charged/discharged limits of an identified SKU.
- Use 8.4 V as the typical 2S full-charge design assumption, subject to the exact pack specification. Do not carry forward the schematic's historical 7S/21–29 V note as the chosen power source.
- Battery sensing remains digital **presence**, with **present = LOW** accepted by the user. It is not a voltage ADC or calibrated undervoltage alarm.
- Amplifier control: hardware defaults OFF; host explicitly enables it. J4.11 / GPIO3_A1 is reserved for active-high AMP_ENABLE in the candidate design. Qwiic pins are not reassigned.
- USB-C and HAT battery sources remain mutually exclusive. No charging circuitry or simultaneous-source support is added.

## Historical stage status before Stage 2 integration

| Stage | Implementation / evidence | Remaining gate |
|---|---|---|
| Recovery baseline | Verified ZIP backup of tracked design made before edits; source HEAD 7f1aef08998dc42486f7f7a647df4b6460282c89 | No commit or push performed |
| BOM purchasing identity | Mixed manufacturer-field aliases resolved; conflicts rejected; exact J4 identity required; J4 required in populated BOM/PnP | New approved clean-commit release must be generated later; historical packages unchanged |
| Power circuit | Promoted and independently rechecked: DMN3023L-7 with manufacturer land, R8.1 to +BATT, C39 CL05B104KB5NNNC 100 nF/50 V | DRC 0, unconnected 0; startup/thermal/VS/VGS/source-removal EVT still required |
| Battery presence | Isolated candidate: NPN collector referenced to host 3.3 V; no raw battery/zener node at GPIO; active LOW | Schematic/PCB validation and powered-off leakage test |
| Amplifier hardware | Isolated candidate: two-NPN default-OFF shutdown circuit, GPIO3_A1 enable | Schematic/PCB validation, early boot pin state and shutdown waveform |
| Amplifier software | Opt-in simple-amplifier/DAPM overlay compiled and applied with DTC 1.7.0 to a synthetic base; pin/phandle/routing readback and missing-card rejection pass | Do not install until matching hardware is promoted; actual kernel/codec/DAPM/mixer/boot validation pending |
| Exact 3D/assembly | Missing J1/J2/J9/J4 bodies and stale Pi host-model reference identified | Exact model acquisition, placement and collision checks remain open |

The active electrical design must not be inferred from the existence of the new
software overlay or a temporary schematic. Candidate-only work is not a completed
PCB change. Update the stage table only after promotion and independent checks.

## Why these changes are needed

1. Q2 Si2312CDS permits ±8 V VGS, but LM5050 specifies up to 9 V at its 5 V drive test condition. Gate-drive and MOSFET ratings must be compatible across conditions, not just on one sample.
2. Before Stage 1, U10 VS derived from the post-Q2 5 V rail via 100 Ω, without margin over its 5 V specified minimum. Stage 1 applies separate battery bias through R8 for low-voltage IN operation; this is not proof of all source-removal behaviors.
3. R24 and a ground-referenced 3.3 V Zener do not establish powered-off GPIO safety. The replacement preserves presence sensing with inverted logic; no claim of galvanic isolation.
4. R3/R4 hardwire PAM8406 shutdown/mute high. Software cannot directly pull those existing nodes low. The new hardware is required before the GPIO overlay can control the amplifier.
5. The former BOM exporter read only `Man.`/`Man. Ref.`; J4 uses `Manufacturer_Name`/`Manufacturer_Part_Number`. Reference presence tests alone did not detect blank purchasing fields.

## Mechanical and external approval gates

- J4 exact MPN stays Toby Electronics REF-182665-01. Its 1.02 × 1.80 mm candidate lands are not claimed as vendor-approved. Obtain vendor/assembler approval or representative assembly validation.
- The Toby product page currently requires login/account access for full CAD assets. Obtain the exact model through authorized access; do not replace it with a visually similar socket.
- J1/J2/J9 use WAGO 2059-302/998-403. Obtain the exact manufacturer's STEP and verify both dimensions and pin-1 orientation. The existing unresolved model path is not evidence of correct 3D placement.
- C45 overlaps the host RK3566 projection in the prior official V1.11 overlay. Confirm at least 4.0 mm board-surface gap, at least 0.5 mm residual clearance, exact header insertion and controlled spacers. Removing this required input bypass is not the default clearance remedy.
- Default to external U.FL antenna; onboard-antenna performance remains unapproved.

## Physical and runtime acceptance

- Establish the exact battery SKU, full-charge voltage, discharge cutoff, pulse-current capability and mating connector polarity. NP-F-style naming alone is insufficient for final electrical limits.
- A buck does not guarantee a stable 5 V rail when a depleted pack approaches 5 V. Battery presence is not an undervoltage monitor; determine a safe operational cutoff separately during EVT.
- Measure U10 VS and Q2 VGS during startup, load steps, battery removal and USB-only operation. Maintain the simultaneous-source prohibition.
- Confirm J4 5 V regulation, startup body-diode stress and 30-minute U9/L4/Q2 thermal behavior at the intended load.
- Confirm unpowered GPIO31 injection/leakage and active-low presence behavior.
- Scope AMP_ENABLE and PAM8406 SHDN throughout power-on, codec failure/success, playback, stop, suspend and shutdown. Validate conservative mixer initialization before enabling playback.
- Keep 8 Ω speakers and a measured audio limit within the 2 A supply envelope. No tested final volume limit exists yet.

## Sources

- TI LM5050-1: https://www.ti.com/lit/ds/symlink/lm5050-1.pdf
- Vishay Si2312CDS: https://www.vishay.com/doc/?65900
- Diodes DMN3023L candidate: https://www.diodes.com/assets/Datasheets/DMN3023L.pdf
- PAM8406: https://www.diodes.com/datasheet/download/PAM8406.pdf
- Nexperia BC847 series: https://assets.nexperia.com/documents/data-sheet/BC847X_SER.pdf
- Official Radxa header: https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface
- Toby exact connector: https://www.toby.co.uk/board-to-board-pcb-connectors/254mm-sockets/ref-raspberry-pi-rpi-hat-specification-connector-surface-mount-sockets/REF-182665-01
- WAGO exact connector: https://www.wago.com/us/pcb-interconnect/smd-pcb-terminal-block-in-tape-and-reel-packaging/p/2059-302_998-403

**fabrication_ready remains false.**

## Historical GPIO/audio candidate — superseded by integrated Stage 2

Isolated candidate:
`C:/Users/juper/AppData/Local/Temp/robot-hat-gpio-candidate/`.
This is **not a manufacturing source**. It must not replace the active PCB
without finishing routing and updating/verifying the exact parity guards.

The candidate uses Q3/Q4/Q5 `BC847B,215`; R24/R42/R46 are 100 kΩ and
R3/R43/R44/R45 are 10 kΩ. R4 remains a zero-ohm MUTE-high connection:
shutdown, not codec volume alone, provides the hardware default-OFF function.
Candidate schematic connectivity tests pass; routing is incomplete.

Two actual routing iterations added 347 segments and 15 vias. Native results:

- Unconnected items: **13 → 5 → 3**.
- Final shorts / copper-clearance violations: **0 / 0**.
- Remaining physical warnings: **14** (7 silk overlaps, 5 silk-over-copper,
  1 dangling track, 1 co-located-hole warning).
- ERC: **0 errors, 46 existing library warnings**.
- Schematic–PCB field warnings: **107**.

Remaining connections are R44.1–Q4.1 and Q4.1–Q5.3 on AMP_INHIBIT, plus a
disconnected GND zone island. Duplicate GND vias at `(116.5, 97.0)` and a
dangling GPIO track starting at `(99.397501, 97.340001)` also need cleanup.
Silk failures involve footprint outlines against existing artwork, not just new
reference labels. The routing search limit is **not proof of physical
infeasibility**; a local placement/routing review is required. Broader local
repositioning of existing small parts was presented as a scope choice, but no
selection was received at this stage.

Evidence: candidate `candidate-evidence/route-2-drc.json`,
`route-final-erc.json`, `routing-final-summary.json`, and
`candidate-evidence/pre-route.kicad_pcb` recovery copy. The active design remains
separate; do not enable the new software overlay on the basis of this candidate.
