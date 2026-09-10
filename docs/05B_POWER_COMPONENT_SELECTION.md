# Power Component Selection — V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × XL330-M288-T  
Last updated: 2026-09-09

## 1. Purpose

Freeze the first practical component candidates for the V1 5 V power architecture before drawing the final KiCad power sheet.

## 2. Radxa host protection

### Candidate: TI TPS25947 family

Reasons:

- 2.7 V to 23 V input range
- 5.5 A class integrated eFuse
- integrated back-to-back FETs
- true reverse-current blocking
- reverse-polarity protection
- adjustable current limit
- adjustable slew rate
- thermal shutdown
- overvoltage/short-circuit protection features
- compact QFN package

This is a strong fit for the +5V_RADXA branch because the HAT can supply the SBC through header pins while USB-C may also be connected.

### Initial host current-limit target

Start design around approximately 4 A current limit, then refine after:

1. Radxa boot/load measurements,
2. audio/peripheral current measurements,
3. thermal simulation/bench test,
4. exact TPS25947 suffix selection.

Do not lock ILIM resistor until the exact device suffix and datasheet equation are confirmed.

## 3. Main 5 V input protection

The servo-system path may experience >10 A transients and potentially 20+ A under pathological load, so the main reverse-polarity protection should not use the TPS25947.

Preferred main-path architecture:

```text
J1 -> F1 -> back-to-back low-RDS(on) MOSFET protection -> +5V_SYS
```

Selection targets:

- effective RDS(on): <=5 mΩ preferred
- VDS rating: >=20 V preferred despite 5 V normal operation
- current handling: >=20 A with PCB thermal support
- package with large exposed copper area
- gate protection / defined off-state

A dedicated ideal-diode controller may be used if it produces a cleaner and safer implementation than discrete control.

Exact MOSFET/controller remains open until package footprint and thermal area are reviewed against the 65 × 30 mm board constraint.

## 4. TVS candidate

### Candidate: Littelfuse SMBJ5.0A

Key characteristics:

- 5.0 V reverse stand-off
- 600 W TVS class
- approximately 9.2 V maximum clamp at rated pulse current

Important limitation:

XL330-M288-T has a maximum operating voltage around 6 V. A conventional 5 V TVS does **not** guarantee that every fast transient remains below 6 V because its clamp voltage is considerably higher under large pulse current.

Therefore the TVS is secondary transient protection only. The system still requires:

- a tightly regulated external 5 V supply,
- short/low-inductance power wiring,
- distributed bulk capacitance,
- potential over-voltage cutoff if tests show meaningful overshoot.

## 5. Main connector

### XT30 candidate

Advantages:

- compact
- polarized
- common in robotics/RC
- plausible for normal MicroDuck operating currents

Risk:

- less margin for prolonged very high current or poor ventilation.

### XT60 candidate

Advantages:

- much more thermal/current margin
- robust for bench testing

Risk:

- large relative to a 65 × 30 mm board.

### V1 direction

Place mechanical priority on XT30 compatibility first. If measured branch current or temperature rise is unacceptable, move to XT60 or remote power-distribution wiring.

## 6. Main fuse

Theoretical simultaneous servo stall plus host load can approach 26 A, but the fuse should protect wiring and board copper rather than permit sustained all-axis stall.

Prototype starting point:

- external/replaceable 15–20 A fuse class
- firmware torque/current limiting
- optional branch protection

Final value depends on:

- wire gauge,
- connector rating,
- actual walking current waveform,
- startup/inrush current,
- acceptable trip behavior.

## 7. Bulk capacitance

Initial distribution:

- servo branch A: 470 µF + 100 µF + 1 µF + 100 nF
- servo branch B: same
- servo branch C: same
- host branch: 470 µF + ceramic bank

Use >=10 V ratings; 16 V electrolytic/polymer parts are preferred where size allows for derating and availability.

## 8. Power-path measurements required before final lock

The prototype must expose measurements for:

- total +5V_SYS current,
- +5V_RADXA current,
- branch A/B/C voltage sag,
- connector temperature,
- protection MOSFET temperature,
- host eFuse temperature.

## 9. Current component status

| Function | Candidate | Status |
|---|---|---|
| Host reverse-current/eFuse | TPS25947 | SELECTED-CANDIDATE |
| Main connector | XT30 | PRIMARY CANDIDATE |
| Alternate connector | XT60 | ALTERNATE |
| Main reverse protection | back-to-back N-MOSFET / ideal diode | SELECTING |
| 5 V TVS | SMBJ5.0A | CANDIDATE |
| Main fuse | 15–20 A replaceable | PROVISIONAL |
| Servo bulk | 3 × 470 µF + local bypass | PROVISIONAL |
| Host bulk | 470 µF + ceramic bank | PROVISIONAL |

## 10. Next engineering action

Before committing the final `power.kicad_sch`:

1. choose the main MOSFET/controller,
2. calculate copper loss for 10 A / 15 A / 20 A,
3. freeze XT30 versus XT60,
4. choose TPS25947 suffix and ILIM network,
5. draw schematic,
6. run ERC,
7. begin placement review.
