# Power Integrity and Source-ORing Review

## Decision

The Radxa port retains the upstream AP63205 2 A buck and LM5050-1/SI2312CDS ideal-diode topology. A 4–5 A redesign is out of scope for the strict port because it would also require a new regulator footprint, inductor, MOSFET, copper geometry and thermal qualification.

The supported configuration is therefore conditional:

- use 8 Ω speakers only;
- keep the PAM8406 muted during Radxa boot;
- establish the final audio gain/volume limit by measuring total +5 V rail current;
- target no more than 1.8 A sustained from the AP63205 path;
- do not apply USB-C power while the HAT battery input is active;
- treat simultaneous-source operation as unsupported until bench backfeed tests pass.

These restrictions are release requirements, not recommendations.

## Evidence and budget

Radxa specifies a 5 V / 2 A power adapter for ZERO 3.[1] The AP63205 is itself a 2 A synchronous buck, so the adapter requirement leaves no guaranteed current allowance for HAT loads.[3]

The PAM8406 can deliver 2 × 1.8 W into 8 Ω at 5 V with roughly 90% efficiency, corresponding to about 0.80 A from +5 V at full sine output. Its 4 Ω condition can reach 2 × 3.14 W at roughly 87% efficiency, or about 1.44 A.[6] Consequently, an 8 Ω speaker requirement alone is insufficient: boot muting and a measured output limit are also mandatory.

Current schematic topology, derived from the committed KiCad netlist:

```text
+BATT -> U9 AP63205 -> L4 -> Net-(D1-K)
Net-(D1-K) -> U10 LM5050-1 + Q2 SI2312CDS -> +5V
+5V -> J4 pins 2/4, PAM8406, LEDs and small support loads
```

The LM5050-1 is intended to drive an external N-channel MOSFET as a low-loss ideal diode and turns it off during reverse-current conditions.[4] This protects the HAT buck path from reverse current at Q2. It does not by itself prove that a powered HAT cannot drive the Radxa USB-C VBUS through the Radxa board; the Radxa schematic and bench measurements remain the authority for that path.[2]

The existing L4 MPN is `SRN6045TA-6R8M`. Its manufacturer rating is higher than the schematic display text “6.8uH/2A”, so the display text must not be used as the component limit; the exact saturation, RMS-current and temperature-rise limits come from the Bourns datasheet.[5]

## Required schematic and layout changes

### 1. High-frequency input bypass

A local X7R capacitor now bypasses U9 VIN to GND. The AP63205 application circuit uses ceramic input decoupling close to the IC.[3]

Implemented layout:

- `C45`: 10 µF, 50 V, X7R, 1210 on B.Cu at `(99.05, 100.95)`, rotation `+90°`;
- nominal part: `Murata GRM32ER71H106KA12L`, LCSC `C77102`.[7]
- short, wide connections use tented 0.6/0.3 mm vias adjacent to U9 VIN and GND;
- C19 remains the bulk input-energy capacitor;
- D1 and C22 were moved locally; U9, L4, Q2 and U10 were not moved;
- the regenerated GND zone and complete local power geometry are hash-locked by the checker;
- native KiCad 10.0.6 DRC reports no new error or warning from the change.

The selected part is 2.5 mm nominal high. Hole-aligned overlay against Radxa's official V1.11 STEP and placement resources maps C45 to approximately Radxa `(28.15, 5.19)` mm, overlapping the host U1/RK3566 package region.[9][10][11] Release therefore requires a measured PCB-surface gap of at least 4.0 mm and at least 0.5 mm residual part-to-part clearance in every intended Radxa SKU. Controlled spacers, not connector friction, must set the gap. If this gate fails, C45 must not be populated on B.Cu.

This power change does not approve operation over Radxa's onboard antenna; use the external U.FL mode or complete OTA validation before release.[12]

### 2. Output transient tuning option

The fitted output bank is `C21 + C22 = 2 × 22 µF nominal`. Their existing MPN `GRM188R61A226ME15D` is a 22 µF, 10 V, X5R, 0603 device; the stale `6V3` display value has been corrected to `10V` without changing the parts or footprints.[8]

The dense strict-port layout does not justify moving unrelated switch-node and test-point routing merely to add a large capacitor. Use a low-ESR 100–330 µF capacitor across the C21/C22 +5 V/GND pads as an EVT tuning option before deciding whether a production footprint is necessary. It is not credited as a complete boot hold-up solution.

For scale:

```text
Delta V = I * Delta t / C
2 A for 1 ms with 0.5 V droop requires 4000 µF.
100 µF at 2 A reaches 0.5 V droop in only 25 µs.
330 µF at 2 A reaches 0.5 V droop in only 82.5 µs.
```

A 100–330 µF option can reduce short load edges and audio crest droop, but cannot replace regulator current margin. Population value and ESR must be selected after load-step testing.

### 3. Power-source rule

Silkscreen and assembly/user documentation must state:

> POWER FROM ONE SOURCE ONLY — disconnect USB-C power before energizing HAT battery input.

No simultaneous-source claim may be made until reverse-current measurements are completed in both voltage orderings.

### 4. Audio startup behavior

The current `R3` and `R4` ties keep PAM8406 SHDN and MUTE asserted high, so the amplifier is enabled at startup. Before production release, firmware or a hardware delay must guarantee muted audio during Radxa boot. If firmware ownership cannot be guaranteed, add a default-off hardware enable network in a separately reviewed change.

## EVT acceptance gates

1. Verify AP63205 output at minimum and maximum supported battery voltage.
2. Capture +5 V at U9/Q2 and at J4 during cold boot with the intended Radxa image and peripherals.
3. Test 0 A to representative load steps; record peak droop, overshoot and recovery.
4. Run 30 minutes at the maximum supported continuous workload and record U9, L4, Q2 and PCB temperatures.
5. Use 8 Ω loads and determine the maximum audio setting that keeps sustained HAT-path current at or below 1.8 A without undervoltage.
6. Test USB-C only, HAT battery only, HAT-first then USB-C, and USB-C-first then HAT while logging current into each source.
7. Fail release if any source sees reverse current beyond its allowed leakage, if Radxa resets, or if thermal limits are exceeded.

## Status

- Architecture decision: **fixed — 2 A strict port**
- Input ceramic layout: **applied and DRC-clean; mechanical gap gate pending**
- Output capacitor metadata: **corrected — 2 × 22 µF / 10 V fitted**
- Additional output bulk: **EVT external/tack option; no production footprint unless test data requires it**
- Silkscreen one-source warning: **applied; native DRC-clean and bottom render checked**
- Audio boot mute: **pending hardware/firmware ownership decision**
- Bench qualification: **pending EVT hardware**
- Production-ready: **no**

## Sources

[1] https://docs.radxa.com/en/zero/zero3/getting-started/preparation — Radxa ZERO 3 power supply requirement
[2] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1110_schematic.pdf — Radxa ZERO 3W V1.11 schematic
[3] https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf — Diodes AP63205 datasheet
[4] https://www.ti.com/lit/ds/symlink/lm5050-1.pdf — TI LM5050-1 datasheet
[5] https://www.bourns.com/docs/product-datasheets/srn6045ta.pdf — Bourns SRN6045TA datasheet
[6] https://www.diodes.com/assets/Datasheets/PAM8406.pdf — Diodes PAM8406 datasheet
[7] https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_muRata_GRM32ER71H106KA12L_10uF-106-10-50V_C77102.html — LCSC C77102 Murata GRM32ER71H106KA12L
[8] https://pim.murata.com/en-us/pim/details?partNum=GRM188R61A226ME15D — Murata GRM188R61A226ME15D product data
[9] https://docs.radxa.com/en/zero/zero3/download — Radxa ZERO 3 official resource downloads
[10] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_3d_stp.zip — Radxa ZERO 3W V1.11 STEP
[11] https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1110_smb.zip — Radxa ZERO 3W V1.11 component placement maps
[12] https://docs.radxa.com/en/zero/zero3/accessories/zero3w-antenna — Radxa ZERO 3W antenna instructions
