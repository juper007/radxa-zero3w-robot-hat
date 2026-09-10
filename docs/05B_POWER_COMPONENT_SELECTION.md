# Power Component Selection — V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × XL330-M288-T  
Last updated: 2026-09-09

## 1. Purpose

Freeze the practical component choices for the V1 5 V power architecture before the final KiCad power sheet and PCB layout.

## 2. Radxa host protection

### Selected candidate: TI TPS25947 family

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

This device is reserved for the +5V_RADXA branch. It is **not** used for the 20 A-class servo input path.

### Host current target

Radxa documentation recommends at least 15 W at 5 V, corresponding to 3 A minimum supply capability. V1 therefore allocates approximately 4 A normal host-branch capacity plus transient margin.

The exact TPS25947 suffix and programming resistors remain to be locked against the latest TI datasheet equations before schematic REVIEW.

## 3. Main 5 V input protection

### Selected controller candidate: TI LM74700-Q1

Reasons:
- 3.2 V to 65 V operating range
- external N-channel MOSFET gate drive
- low-loss ideal-diode behavior
- reverse-current blocking
- reverse-polarity protection
- small package

### Selected MOSFET candidate: Infineon BSC009NE2LS5I

Key parameters used for V1 design:
- VDS: 25 V
- SuperSO8 5 × 6 mm package
- max RDS(on) about 1.35 mΩ at VGS = 4.5 V

Conservative 20 A conduction estimate:
- voltage drop ≈ 27 mV
- MOSFET conduction loss ≈ 0.54 W

This makes the external MOSFET far more appropriate for the main servo rail than a 5.5 A integrated eFuse.

## 4. Input connector

### V1 decision: XT60-class

The previous XT30-first direction is superseded for the initial prototype.

Reason:
- theoretical 15-servo stall current is about 22.05 A,
- development testing should not operate close to connector limits,
- XT60-class input gives more margin for transient and bench fault testing.

If board-mounted XT60 is too large for the final mechanical stack, use heavy solder pads and a short XT60 pigtail rather than shrinking the electrical rating prematurely.

XT30 may be reconsidered only after measured robot current confirms adequate thermal margin.

## 5. TVS strategy

### Candidate: Littelfuse SMBJ5.0A

Important limitation:
- conventional 5 V TVS clamp voltage can exceed the XL330 recommended/maximum operating envelope during a strong pulse.

Therefore TVS is supplementary protection only. V1 also relies on:
- tightly regulated external 5 V PSU,
- short low-inductance wiring,
- distributed bulk capacitance,
- optional active over-voltage cutoff if transient testing shows a need.

TVS selection remains CANDIDATE rather than LOCKED.

## 6. Main fuse

Prototype target:
- 20 A class replaceable fuse

The fuse protects wiring and board copper against sustained faults. It is not intended to make simultaneous 15-servo stall a valid continuous operating condition.

Final value depends on:
- PSU current limiting,
- cable gauge,
- XT60 implementation,
- measured walking waveform,
- nuisance-trip behavior.

## 7. Bulk capacitance

Initial distribution:
- SERVO_A: 470 µF + 100 µF + 1 µF + 100 nF
- SERVO_B: same
- SERVO_C: same
- +5V_RADXA: 470 µF + ceramic bank

Use 10 V minimum; 16 V bulk capacitors are preferred where size permits.

## 8. Servo branch topology

V1 power distribution is split into three nominal groups:

- SERVO_A: 5 motors
- SERVO_B: 5 motors
- SERVO_C: 5 motors

Theoretical stall current per branch is 7.35 A. Branch copper and power connectors must therefore tolerate short events beyond 7 A with margin.

## 9. Copper requirement

V1 prototype PCB target:
- 4 layers
- 2 oz outer copper preferred
- full-current input trunk implemented as large pours, not traces
- target >=15 mm effective 2 oz width over a short path where practical
- top/bottom parallel copper plus dense via stitching

See `05C_HIGH_CURRENT_LAYOUT_AND_PROTECTION.md` for loss calculations.

## 10. Current component status

| Function | Candidate | Status |
|---|---|---|
| Host reverse-current/eFuse | TPS25947 family | SELECTED-CANDIDATE |
| Main reverse controller | LM74700-Q1 | SELECTED-CANDIDATE |
| Main MOSFET | BSC009NE2LS5I | SELECTED-CANDIDATE |
| Main connector | XT60-class / pigtail | V1 DECISION |
| Main fuse | 20 A replaceable | PROVISIONAL |
| 5 V TVS | SMBJ5.0A | CANDIDATE |
| Servo bulk | 3 × (470 µF + 100 µF + ceramics) | PROVISIONAL |
| Host bulk | 470 µF + ceramics | PROVISIONAL |
| PCB outer copper | 2 oz preferred | V1 DECISION |

## 11. Next engineering action

1. freeze TPS25947 suffix and ILIM/dVdt values,
2. define the complete reference-designator/net connectivity list,
3. create the KiCad power sheet,
4. perform ERC,
5. verify actual footprint geometry,
6. start placement review.

**Not fabrication-ready.**
