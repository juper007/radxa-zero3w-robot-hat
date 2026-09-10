# KiCad Power Sheet Implementation Spec

Target file: `hardware/kicad/power.kicad_sch`  
Status: DESIGNING

This file is the implementation contract for the V1 power schematic.

## Sheet ports

### Inputs
- `VIN_RAW`
- `GND`

### Outputs
- `MOTOR_VBUS`
- `+5V_RADXA`
- `+3V3_LOGIC` is not generated here; it is supplied by the Radxa host where needed.

### Optional control/status
- `PWR_EN`
- `PWR_GOOD`

## Block A — main input

Recommended topology:

```text
J1 VIN+
  |
 F1
  |
 reverse-polarity / ideal-diode element
  |
  +---- D_TVS ---- GND
  |
 MOTOR_VBUS
```

Place the TVS and first bulk capacitor physically close to J1.

### Nets
- `VIN_RAW`: connector-side input before protection
- `VIN_FUSED`: after fuse
- `MOTOR_VBUS`: protected main rail

## Block B — motor rail bulk

Initial population:
- `C_M1` = 470 uF, voltage rating chosen after VIN freeze
- `C_M2` = 100 uF
- `C_M3` = 1 uF ceramic
- `C_M4` = 100 nF ceramic

All capacitors connect `MOTOR_VBUS` to GND.

Provide at least one large-cap footprint that can accept a higher-capacitance alternate during prototype tuning.

## Block C — 5 V synchronous buck

```text
MOTOR_VBUS
    |
  CIN bank
    |
 U_BUCK ---- SW ---- L1 ---- +5V_PRE
    |                         |
   GND                       COUT
                              |
                             GND
```

Feedback divider senses the regulated output after L1/COUT. Follow the selected regulator's reference layout exactly for the hot-loop components.

### Required features
- input rating above final VIN maximum
- practical 5 A output target
- current limiting
- thermal shutdown
- UVLO
- enable pin

### PCB implementation rule
The regulator, input ceramics, switching node and inductor must be placed before general PCB routing begins.

## Block D — 5 V host isolation / backfeed option

Prototype topology:

```text
+5V_PRE --> [U_LOAD / ideal diode option] --> +5V_RADXA
                      |
                 configuration pads
```

Provide a configurable footprint so that:
1. reverse-current blocking can be populated for initial testing;
2. it can later be bypassed with a 0-ohm link only after USB-C coexistence is validated.

Do not hard-short `+5V_PRE` to Radxa pins 2/4 in the first prototype without a deliberate configuration point.

## Block E — Radxa header power pins

- Physical pin 2 -> `+5V_RADXA`
- Physical pin 4 -> `+5V_RADXA`
- Physical pins 6,9,14,20,25,30,34,39 -> GND
- Physical pins 1,17 are Radxa 3.3 V and are not driven by this power sheet.

## Block F — test points

- `TP1` VIN_RAW
- `TP2` MOTOR_VBUS
- `TP3` +5V_PRE
- `TP4` +5V_RADXA
- `TP5` GND
- `TP6` BUCK_EN

Optional:
- `TP7` PWR_GOOD
- small scope pad at SW node, marked `SW_SCOPE_ONLY`

## ERC conventions

Use explicit power flags only where required by KiCad ERC. Avoid hiding genuine power-source ambiguity with excessive `PWR_FLAG` symbols.

## Net classes

Create at least:

### `MOTOR_POWER`
- Nets: VIN_RAW, VIN_FUSED, MOTOR_VBUS
- Wide copper / pours
- Conservative via arrays for layer transitions

### `HOST_5V`
- Nets: +5V_PRE, +5V_RADXA
- Sized for 5 A design target

### `SIGNAL`
- EN, PG, feedback-related control signals

Do not route the feedback trace adjacent to or underneath the switching node.

## Placement priority

1. J1 + fuse + reverse protection
2. TVS + motor bulk capacitors
3. buck IC + input ceramics
4. inductor + output capacitor bank
5. 5 V reverse-current block
6. Radxa 40-pin header
7. test points

## Schematic review checklist

- [ ] No 5–28 V rail reaches Radxa 5 V pins directly
- [ ] Reverse polarity protection orientation correct
- [ ] TVS polarity and voltage rating correct
- [ ] All bulk-cap voltage ratings valid
- [ ] Buck IC absolute max > design VIN
- [ ] Inductor saturation current exceeds worst-case peak
- [ ] Feedback divider produces intended output
- [ ] EN pin has a defined state
- [ ] Host 5 V path has configurable backfeed protection
- [ ] Ground pins present and connected
- [ ] Test points present
- [ ] ERC passes

## Layout review checklist

- [ ] Input hot loop minimized
- [ ] Switch-node copper kept compact
- [ ] Feedback routed away from SW
- [ ] Solid ground under regulator except where datasheet says otherwise
- [ ] Thermal pad via pattern follows regulator datasheet
- [ ] Motor current return does not cross audio/logic section
- [ ] Power connector and motor connector copper sized from current budget

The exact component references and footprints will be frozen after regulator/protection part selection.
