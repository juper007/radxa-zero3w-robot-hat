# Power Schematic Values — V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × XL330-M288-T  
Last updated: 2026-09-09

## 1. Frozen V1 architecture

V1 uses one regulated external 5 V high-current supply. The HAT does not perform a 12–28 V to 5 V high-power conversion.

```text
5V IN (XT60-class)
   |
  Fuse
   |
LM74700-Q1 + external N-MOSFET ideal diode
   |
 +5V_SYS
   +--> Servo branch A (5 servos)
   +--> Servo branch B (5 servos)
   +--> Servo branch C (5 servos)
   +--> TPS259470A eFuse --> +5V_RADXA --> header pins 2/4
```

## 2. Main ideal-diode controller

Selected controller: **LM74700QDBVRQ1** (6-pin SOT-23 package family).

External MOSFET candidate: **BSC009NE2LS5I**.

Required LM74700 support values for V1:

- C_VCAP = 100 nF from VCAP to ANODE.
- C_IN_LOCAL = 22 nF minimum from ANODE/input side to GND, located close to U1.
- C_OUT_LOCAL = 100 nF minimum from CATHODE/output side to GND, located close to U1.
- EN is held high from the protected/raw input side for normal operation; add a solder-jumper/test point if shutdown control is desired during bring-up.
- ANODE and CATHODE Kelvin/sense connections must not share thin sense traces with the high-current power path.

The MOSFET orientation and ANODE/CATHODE routing must follow the LM74700 ideal-diode topology exactly. Do not infer source/drain orientation from generic reverse-polarity MOSFET examples.

## 3. Radxa branch eFuse

Selected device for first schematic: **TPS259470ARPWR**.

Why this suffix:

- adjustable OVLO,
- active current limiting,
- auto-retry after a fault,
- true reverse-current blocking,
- better behavior for a computer load than a permanently latched-off prototype after a transient overload.

If bench testing shows repeated retry oscillation under a hard fault is undesirable, the latch-off `TPS259470LRPWR` variant remains a drop-in functional alternative for the same design family.

## 4. TPS259470A current limit

The datasheet electrical table shows approximately inverse proportionality between RILM and ILIM:

- 750 Ω → ~4.45 A typical,
- 1.65 kΩ → ~2.03 A typical,
- 3.32 kΩ → ~1.01 A typical.

For the V1 target of roughly 4 A nominal current limit:

- **R_ILM = 825 Ω (1%)**
- expected typical threshold ≈ 4.05 A

This is below the device 5.5 A continuous switch-current recommendation while leaving margin above the Radxa 15 W-class requirement.

Do not treat 4.05 A as an exact protection threshold; the datasheet specifies tolerance and the final acceptance criterion must include bench measurement.

## 5. TPS259470A output slew rate

Chosen host-rail target: approximately 10 ms to rise from 0 to 5 V.

Desired slew rate:

`SR = 5 V / 10 ms = 0.5 V/ms`

Datasheet relationship:

`CdVdt(pF) = 2000 / SR(V/ms)`

Therefore:

`CdVdt ≈ 4000 pF`

Selected standard value:

- **C_DVDT = 3.9 nF**

Expected 5 V rise time is approximately 9.75 ms. Because this value is below 10 nF, the datasheet's recommended 100 Ω series resistor for CdVdt > 10 nF is not required.

## 6. TPS259470A over-voltage lockout

V1 input is intended to be a tightly regulated 5 V source. Set host OVLO near 5.7 V so an abnormal external supply cannot be passed to the Radxa branch indefinitely.

The OVLO threshold is approximately 1.2 V. A divider of:

- R_OV_TOP = **374 kΩ, 1%**
- R_OV_BOTTOM = **100 kΩ, 1%**

gives a nominal threshold:

`5.7 V ≈ 1.2 V × (374k + 100k) / 100k`

The threshold must be verified with actual resistor tolerance and device OVLO threshold tolerance before fabrication release.

## 7. TPS259470A enable / UVLO

V1 does not need a custom high UVLO threshold because the system is supplied by a regulated 5 V source. EN/UVLO will therefore be enabled from +5V_SYS through a high-value resistor consistent with the datasheet reverse-polarity guidance.

Initial value:

- **R_EN = 390 kΩ** from +5V_SYS to EN/UVLO.

Add a test pad on EN/UVLO and an optional footprint to pull EN low during bring-up.

## 8. Host output capacitance

Initial population on +5V_RADXA:

- 470 µF low-ESR bulk capacitor, 10 V or 16 V rated,
- 2 × 22 µF X7R ceramic, 10 V or higher,
- 1 × 1 µF ceramic,
- 1 × 100 nF ceramic.

The large capacitor is after the reverse-blocking eFuse so USB-C coexistence testing can be performed without the HAT bulk capacitor discharging back into the source side.

## 9. Servo branch capacitors

Each 5-servo branch starts with:

- 470 µF low-ESR, 10/16 V,
- 100 µF low-ESR,
- 1 µF ceramic,
- 100 nF ceramic.

These values are provisional and may be changed after measuring walking-current pulses and cable-induced ringing.

## 10. Main fuse and connector

Prototype direction:

- XT60-class polarized input connector.
- Replaceable external or PCB-accessible **20 A nominal fuse** as a starting point.

The 20 A value is not intended to permit sustained 15-servo simultaneous stall. It protects wiring/board against gross faults while firmware torque/current limits and servo protection prevent pathological sustained loading.

## 11. TVS

Keep a TVS footprint on the 5 V system rail, but do not rely on a conventional SMBJ5.0A alone to guarantee the XL330 rail stays below 6 V during every pulse. The final TVS/OVP decision remains a validation item because conventional 5 V TVS clamp voltage is significantly higher than 6 V under large pulse current.

## 12. PCB rules that are now schematic requirements

- Outer copper: 2 oz target.
- Main +5V_SYS path: polygon/pour, not a thin routed trace.
- Use top and bottom copper in parallel for the high-current corridor.
- Dense via stitching at connector, fuse, MOSFET, and branch split points.
- Do not route Radxa/audio current through the servo return-current corridor.
- Place U1/Q1 close to the input connector and fuse.
- Place U2 close to header pins 2/4 but outside the servo branch current path.

## 13. Open validation items

- Confirm BSC009NE2LS5I source/drain pad orientation in the selected KiCad footprint.
- Confirm LM74700 package variant/pin numbering before footprint lock.
- Bench-measure TPS259470A current limit with 825 Ω.
- Bench-measure +5V_RADXA ramp with 3.9 nF dVdt capacitor.
- Verify OVLO trip/recovery around the intended 5.7 V threshold.
- Verify simultaneous USB-C + HAT power behavior.
- Verify motor regenerative transients on +5V_SYS.

## 14. Fabrication rule

This file freezes the **first schematic values**, not the fabrication release. The power section remains DESIGNING until KiCad ERC and hardware review are complete.
