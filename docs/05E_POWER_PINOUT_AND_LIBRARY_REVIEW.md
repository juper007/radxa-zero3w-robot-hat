# Power Pinout and KiCad Library Review — V1

Status: REVIEW-IN-PROGRESS  
Date: 2026-09-09

## Purpose

Freeze verified electrical pin maps for the custom KiCad power symbols before graphical schematic completion. This review found and corrected a source/drain orientation error in the earlier connectivity draft.

## LM74700QDBVRQ1 — DBV 6-pin SOT-23

Verified against TI LM74700-Q1 datasheet, DBV package top view:

| Pin | Name | V1 use |
|---:|---|---|
| 1 | VCAP | 100 nF charge-pump capacitor to ANODE |
| 2 | GND | system ground |
| 3 | EN | enabled from input side; optional bring-up control |
| 4 | CATHODE | Kelvin sense of protected output / Q1 drain side |
| 5 | GATE | external N-MOSFET gate |
| 6 | ANODE | input power Kelvin sense / Q1 source side |

Critical topology rule: for the external N-channel MOSFET in the LM74700 ideal-diode configuration, **ANODE connects to MOSFET SOURCE and CATHODE connects to MOSFET DRAIN**. The previous draft connectivity table had the MOSFET source/drain labels reversed; that error has been corrected.

## BSC009NE2LS5I — PG-TDSON-8 / SuperSO8

Verified against Infineon datasheet:

| Pin(s) | Function |
|---|---|
| 1, 2, 3 | Source |
| 4 | Gate |
| 5, 6, 7, 8 | Drain |

V1 connection:

- pins 1–3 SOURCE -> F1_OUT / LM74700 ANODE side
- pin 4 GATE -> LM74700 GATE
- pins 5–8 DRAIN -> +5V_SYS / LM74700 CATHODE side

## TPS259470ARPWR — RPW 10-pin QFN

Verified against TI TPS25947 Rev. C datasheet:

| Pin | Name for TPS259470x | V1 use |
|---:|---|---|
| 1 | EN/UVLO | 390 kΩ enable network + test point |
| 2 | OVLO | 374 kΩ / 100 kΩ divider |
| 3 | AUXOFF | status/test exposure; open-drain |
| 4 | FLT | fault test point; open-drain |
| 5 | IN | +5V_SYS |
| 6 | OUT | +5V_RADXA |
| 7 | DVDT | 3.9 nF to GND |
| 8 | GND | system ground |
| 9 | ILM | 825 Ω to GND |
| 10 | ITIMER | left open in first V1 pass unless transient blanking is intentionally enabled |

## Current-limit note

TI's May-2026 datasheet table lists typical active-current-limit examples including 4.452 A at RILM=750 Ω. The 825 Ω value remains a calculated ~4.05 A nominal target and must be treated as a calculated design point, not a guaranteed exact threshold. Bench validation is mandatory.

## KiCad library files

Project-specific symbols are now stored in:

- `hardware/libraries/radxa_robot_hat_power.kicad_sym`
- registered from `hardware/kicad/sym-lib-table`

Symbols currently defined:

- `LM74700QDBVRQ1`
- `TPS259470ARPWR`
- `BSC009NE2LS5I`

## Validation policy

The pin map above is the authoritative V1 source for custom symbol pin numbering. Before fabrication release:

1. open all three symbols in KiCad 9,
2. visually compare each pin number/name against the manufacturer package drawing,
3. verify every footprint pad number against the package drawing,
4. run KiCad ERC,
5. run PCB DRC after footprint assignment,
6. independently review Q1 source/drain orientation at schematic and PCB levels.

The existence of a `.kicad_sym` or `.kicad_sch` file does not imply fabrication readiness.
