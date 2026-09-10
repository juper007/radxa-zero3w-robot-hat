# Power Subsystem Design — V1

Status: DESIGNING  
Target: Radxa ZERO 3W Robot HAT V1  
Last updated: 2026-09-09

## 1. Goal

Design a robust power subsystem for a Radxa ZERO 3W based MicroDuck-style robot HAT. The board must accept the robot/motor supply, pass that rail to the Dynamixel bus, generate a clean 5 V rail for the Radxa host and low-voltage electronics, and avoid destructive backfeed or transient behavior.

This document intentionally separates **motor VBUS** from the **regulated 5 V host rail**. The original Pollen Robot HAT is used as the architectural reference, but this project will re-validate the design for the Radxa ZERO 3W rather than copy it blindly.

## 2. Power domains

### 2.1 VIN / MOTOR_VBUS

- External robot supply input.
- Design envelope: 5–28 V input capability at connector/protection level.
- Primary use: Dynamixel motor bus power.
- Must tolerate motor current transients and cable inductance.
- Must not be tied directly to Radxa 5 V pins.

### 2.2 +5V_RADXA

- Regulated 5 V rail generated from VIN.
- Feeds Radxa ZERO 3W through 40-pin header pins 2 and 4.
- Also feeds 5 V peripherals when appropriate.
- Target continuous capability: **5 A design target**, subject to final regulator/thermal validation.
- Output setpoint target: 5.1 V nominal to allow modest distribution drop while remaining within host tolerance; final value must be confirmed against Radxa power requirements before fabrication.

### 2.3 +3V3_LOGIC

- Prefer Radxa-provided 3.3 V for light logic loads only.
- Do not power motors or high-current loads from Radxa 3.3 V.
- Add local decoupling at every logic IC.

## 3. Proposed V1 power tree

```text
External Supply
      |
      v
[Input connector]
      |
[Reverse polarity / ideal diode]
      |
[TVS + surge clamp]
      |
[Bulk capacitance]
      |
      +-------------------------> MOTOR_VBUS -> Dynamixel connectors
      |
      +--> [5 V synchronous buck] --> +5V_RADXA --> 40-pin pins 2,4
                                      |
                                      +--> audio / low-voltage peripherals
```

## 4. Input protection

### 4.1 Reverse-polarity protection

Preferred implementation: P-channel MOSFET or ideal-diode/high-side controller sized for the final motor current.

Requirements:
- Low RDS(on) to minimize voltage drop and heat.
- Voltage rating >= 40 V preferred for a nominal 28 V maximum design envelope.
- Current rating with comfortable margin above expected robot current.

A simple series Schottky diode is not preferred for the main motor rail because loss scales poorly at several amperes.

### 4.2 TVS protection

Place a unidirectional TVS from protected VIN to GND near the power connector.

Selection constraints:
- Standoff voltage above maximum intended supply voltage.
- Clamp voltage below the downstream component absolute maximum where practical.
- Sufficient pulse rating for motor/cable transients.

Exact TVS part remains TBD until the actual robot battery/supply voltage is frozen.

### 4.3 Fuse / resettable protection

V1 should provide a footprint for input over-current protection.

Preferred options:
- Replaceable fuse for predictable fault protection, or
- High-current resettable PTC if final current allows acceptable resistance/thermal behavior.

For the prototype, a conventional fuse footprint is preferred over depending only on a PTC.

## 5. Motor rail filtering

Motor VBUS must have local energy storage near the Dynamixel output connectors.

Initial target population:
- 1 × 470 µF low-ESR electrolytic/polymer bulk capacitor
- 1 × 100 µF low-ESR bulk capacitor
- 1 × 1 µF ceramic
- 1 × 100 nF ceramic

All voltage ratings must exceed maximum MOTOR_VBUS with margin. If 28 V operation is retained, bulk capacitors should normally be rated 35 V minimum; 50 V may be preferable depending on transient testing.

## 6. 5 V regulator architecture

### 6.1 Requirements

The host regulator should be a synchronous buck converter with:
- Input capability covering the finalized VIN range.
- 5 V output.
- >= 5 A practical output capability.
- Current limiting.
- Thermal shutdown.
- UVLO.
- Good transient response.
- Enable pin preferred.

### 6.2 Current recommendation

Do **not** finalize a regulator only from headline current rating. The chosen device must be validated at the worst expected VIN, 5 V output, actual PCB copper area, ambient temperature, and expected Radxa peak load.

V1 footprint selection will prioritize a modern synchronous buck family with enough voltage headroom for 24–28 V systems. Candidate families should be compared in the BOM before lock.

### 6.3 Output network

Initial target:
- Ceramic output bank sized per regulator datasheet.
- Additional 220–470 µF low-ESR bulk near the 40-pin 5 V injection point if transient testing shows benefit.
- Kelvin feedback routing.
- Short switching loop.

## 7. Backfeed protection

This is a critical V1 requirement.

The Radxa may also be connected to USB-C while the HAT is supplying 5 V through pins 2/4. The HAT must not create an unsafe uncontrolled source-to-source path.

Design rule:
- Treat HAT 5 V injection and Radxa USB-C input coexistence as a specific validation item.
- Do not assume the SBC includes sufficient reverse-current blocking.
- Provide an optional load-switch / ideal-diode footprint or 0-ohm configuration point in the HAT 5 V path so the prototype can be tested safely before the connection is permanently simplified.

Prototype configuration should favor protection over minimum BOM count.

## 8. Grounding

Use one common electrical ground, but control current return paths physically.

Layout rules:
- Motor-current returns should go directly to the input/bulk capacitor region.
- Buck power loop should be compact.
- Audio/codec ground area should not sit in the motor return path.
- Inner-layer solid GND plane is preferred.
- Do not split the ground plane under high-speed digital signals unless there is a verified reason.

## 9. PCB current strategy

Target board: 4 layers.

Recommended stack intent:
1. L1 — components/signals + local power copper
2. L2 — solid GND
3. L3 — power distribution / signals
4. L4 — components/signals + power copper

MOTOR_VBUS must use copper pours rather than narrow traces. Final width must be calculated from actual copper weight, temperature rise target, connector rating, and expected maximum simultaneous servo current.

## 10. Connectors

Power-input connector requirements:
- Mechanically keyed/polarized preferred.
- Rated above final continuous current.
- Voltage rating >= maximum VIN.
- Accessible after HAT installation.

Dynamixel power path connectors must be sized using the same current budget rather than only the single-servo current.

## 11. Test points

Mandatory test points:
- TP_VIN_RAW
- TP_MOTOR_VBUS
- TP_5V_RADXA
- TP_3V3
- TP_GND
- TP_BUCK_EN

Recommended measurement pads:
- Regulator SW node pad for oscilloscope probing, physically small and clearly marked.
- Feedback test pad only if it does not compromise noise performance.

## 12. Bring-up sequence

1. Assemble power section only or keep downstream loads disconnected.
2. Check resistance from VIN and 5 V rails to GND before power-up.
3. Power from current-limited bench supply at low voltage.
4. Verify reverse-polarity protection behavior.
5. Verify +5V_RADXA no-load voltage.
6. Load test 5 V rail incrementally: 0.5 A, 1 A, 2 A, 3 A, then higher as thermal limits allow.
7. Measure ripple and load transient response.
8. Verify no abnormal current when USB-C and HAT power coexist.
9. Connect Radxa without Dynamixel servos.
10. Only after host stability is confirmed, connect motor bus and servos.

## 13. Thermal acceptance

Before fabrication release, estimate and then measure:
- Regulator IC temperature.
- Inductor temperature.
- Reverse-protection MOSFET temperature.
- Input connector temperature.
- Motor power connector temperature.

Initial design target: no component should operate close to absolute thermal limits during sustained expected load. A minimum 20% current/thermal headroom is preferred where practical.

## 14. V1 provisional BOM classes

| Ref class | Function | Initial requirement | Status |
|---|---|---|---|
| J_PWR | Main input | 5–28 V, high-current | SELECTING |
| F1 | Input fuse | high-current, replaceable | SELECTING |
| Q1 / U_PROTECT | Reverse protection | >=40 V, low-loss | SELECTING |
| D_TVS | Input transient clamp | voltage TBD after VIN freeze | SELECTING |
| C_BULK | Motor rail bulk | 470 µF + 100 µF initial | PROVISIONAL |
| U_BUCK | Radxa 5 V regulator | synchronous, >=5 A practical | SELECTING |
| L_BUCK | Buck inductor | per selected regulator | TBD |
| C_IN/C_OUT | Buck capacitors | per selected regulator | TBD |
| U_LOAD | 5 V backfeed protection | optional/DNP-capable | PROVISIONAL |

## 15. Open decisions before schematic lock

- Freeze normal robot supply voltage and absolute input envelope.
- Calculate worst-case current for the 15-servo XL330 bus.
- Select exact regulator and inductor.
- Select input connector family.
- Decide whether 5 V reverse-current protection is mandatory-populated or prototype-only.
- Verify Radxa 5 V pin injection and simultaneous USB-C behavior from official documentation/testing.

## 16. Exit criteria

Power schematic can move from DESIGNING to REVIEW when:
- Exact regulator selected.
- Exact protection parts selected.
- Current budget documented.
- Capacitor voltage ratings locked.
- Connector current ratings verified.
- Backfeed strategy represented in schematic.
- ERC passes.
- Reviewer checklist completed.

**Do not fabricate from this document alone.** This is the electrical design specification for the upcoming KiCad power sheet.
