# Power Subsystem Design — V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × DYNAMIXEL XL330-M288-T  
Last updated: 2026-09-09

## 1. Goal

Design a robust power subsystem for a Radxa ZERO 3W based MicroDuck-style robot HAT.

The original upstream Robot HAT supports a broad robot-power concept, but this project is optimized for the actual V1 actuator set: 15 × XL330-M288-T. Because both the Radxa ZERO 3W and XL330-M288-T are 5 V-class devices, the V1 power architecture is intentionally simplified to use an **external regulated 5 V high-current supply**.

See `05A_POWER_CURRENT_BUDGET.md` for detailed current calculations.

## 2. V1 design decision

### Primary input

- Nominal input: **5.0 V regulated**
- Target external supply class: 15–20 A for development
- Higher-current bench supply optional for transient/stall validation
- Main board is **not** intended to convert 12–28 V down to the full servo-system current in V1

### Why

At 5 V, a single XL330-M288-T can draw about 1.47 A at stall. Fifteen simultaneous stalls correspond to approximately 22.05 A before adding the Radxa and peripherals.

A compact HAT-mounted 12–28 V → 5 V converter sized for this full load would create unnecessary thermal, EMI, cost and layout difficulty.

## 3. Power domains

### 3.1 +5V_IN

External regulated 5 V robot supply after the physical input connector but before protection.

### 3.2 +5V_SYS

Main protected 5 V system rail after fuse/reverse-polarity protection.

### 3.3 +5V_SERVO

High-current branch distributed to XL330 connectors.

Requirements:
- Large copper area
- Very low resistance
- Bulk capacitance near connector groups
- Branch distribution preferred over daisy-chaining the entire load through one thin path

### 3.4 +5V_RADXA

Protected/filtered host branch derived from +5V_SYS.

Feeds Radxa ZERO 3W through 40-pin header pins 2 and 4.

Host branch design allocation: up to approximately 3–4 A including selected peripherals, with final current limit based on chosen protection device.

### 3.5 +3V3_LOGIC

Use Radxa 3.3 V for low-current logic only where appropriate.

Do not use the Radxa 3.3 V rail for motors or high-current loads.

## 4. V1 power tree

```text
External regulated 5 V / high-current supply
                 |
            [Main connector]
                 |
            [Main fuse]
                 |
     [Reverse-polarity protection]
                 |
              +5V_SYS
          _______|________________
         |                        |
         v                        v
   +5V_SERVO               Host protection/filter
         |                        |
  Servo branch A/B/C        +5V_RADXA
                                  |
                           Radxa header pins 2/4
                                  |
                           Audio / low-power 5 V
```

## 5. Input connector

The input connector must be selected for actual current and wire gauge.

Evaluation targets:

- XT30: compact, plausible for moderate-current prototype use
- XT60: larger but more comfortable current/thermal margin
- High-current pluggable terminal: serviceable but mechanically larger

Final choice must be based on mechanical fit, connector temperature rise and available wire gauge.

## 6. Main protection

### 6.1 Fuse

Provide a replaceable main fuse or equivalent serviceable over-current protection.

The main fuse protects the board and upstream wiring, not individual servo leads.

Branch protection may be added for groups of servos.

### 6.2 Reverse-polarity protection

Preferred implementation:

- Low-RDS(on) P-channel/N-channel ideal-diode style MOSFET architecture, or
- Dedicated ideal-diode / reverse-input controller if layout and BOM justify it

At 10–20 A, resistance matters significantly. A simple series diode is not preferred.

### 6.3 TVS / transient clamp

For a regulated 5 V input, the TVS selection should be optimized around a 5 V system rather than a 28 V envelope.

The exact TVS part must be selected so its standoff/clamp behavior does not interfere with normal 5 V operation while protecting downstream devices from cable/motor transients.

## 7. Servo power distribution

### 7.1 Branching

Preferred topology:

- Servo branch A
- Servo branch B
- Servo branch C

Each branch should feed a subset of the 15 actuators so the entire current does not pass through one connector/trunk segment.

### 7.2 Bulk capacitance

Place bulk capacitance near the servo distribution region.

Initial prototype target:

- Multiple low-ESR 470 µF capacitors distributed near servo groups
- 100 µF local bulk where useful
- 1 µF ceramic per branch region
- 100 nF ceramic for high-frequency bypass

Because the system is 5 V, use capacitor voltage ratings with generous margin, typically 10 V or greater; 16 V parts are attractive for availability and derating.

### 7.3 PCB copper

Do not represent +5V_SERVO as an ordinary signal trace.

Use:

- copper pours,
- multiple layers where beneficial,
- dense via stitching between parallel power areas,
- short connector-to-bulk paths,
- direct low-impedance return to supply entry.

Final copper requirement must be checked against board copper weight and measured temperature rise.

## 8. Radxa host branch

Radxa ZERO 3W is a 5 V-only SBC. The host branch must remain isolated from major servo current paths even though all rails share a common electrical ground.

Host branch should include:

- independent current protection or eFuse/load switch,
- local bulk capacitance,
- ceramic bypass,
- optional ferrite/LC filtering if testing shows servo noise coupling,
- explicit test points.

## 9. USB-C / header backfeed risk

This remains a critical validation item.

The Radxa may be connected to USB-C while the HAT also injects 5 V through header pins 2/4.

Do not assume safe reverse-current isolation exists inside the SBC.

V1 shall preserve a configurable protection point in the +5V_RADXA branch using one of:

- reverse-current blocking load switch,
- ideal-diode device,
- protected eFuse,
- removable 0-ohm configuration jumper only after validation.

Prototype default must favor protection.

## 10. Grounding

Use a common ground plane, but control physical return-current flow.

Layout rules:

- Servo return enters/returns close to the main input and bulk region.
- Host/audio area must not sit in the primary servo current-return path.
- Prefer a solid inner GND plane.
- Stitch high-current return regions with many vias.
- Avoid narrow necks in GND copper.

## 11. PCB stack intent

Target: 4-layer PCB.

1. L1 — components/signals + heavy local 5 V copper
2. L2 — solid GND
3. L3 — +5 V distribution / secondary signals
4. L4 — components/signals + heavy local 5 V copper

For the servo rail, parallel copper on L1/L3/L4 may be used where routing and thermal analysis support it.

## 12. Test points

Mandatory:

- TP_5V_IN
- TP_5V_SYS
- TP_5V_SERVO_A
- TP_5V_SERVO_B
- TP_5V_SERVO_C
- TP_5V_RADXA
- TP_3V3
- multiple GND probe pads

Optional:

- current-shunt footprint or removable jumper for measuring total servo current
- host current measurement point

## 13. Bring-up sequence

1. Populate power/protection section only.
2. Verify resistance to GND before power-up.
3. Power from current-limited 5 V bench supply.
4. Verify reverse-input behavior.
5. Verify +5V_SYS.
6. Verify host protection behavior with Radxa disconnected.
7. Load-test +5V_RADXA at 0.5 A, 1 A, 2 A, 3 A.
8. Check ripple and voltage sag.
9. Test HAT power + USB-C coexistence before normal use.
10. Connect Radxa without servos.
11. Connect one servo branch with one actuator.
12. Expand actuator count gradually while logging voltage/current.
13. Test aggressive multi-axis motion.
14. Measure connector, MOSFET and copper temperatures.

## 14. Design targets

### Host rail

- 5 V nominal
- Keep voltage drop low enough for stable SBC operation
- 3–4 A protected branch design envelope

### Servo rail

- 5 V nominal
- Development system target: 15–20 A supply capability
- Theoretical 15-servo stall: ~22.05 A
- Firmware must prevent sustained simultaneous stall

## 15. Deferred feature: universal high-voltage input

A later revision may support 12–28 V input with an external or board-level high-power 5 V converter.

That is explicitly out of scope for the compact MicroDuck-optimized V1 unless mechanical/electrical testing demonstrates a compelling need.

## 16. Open items before schematic lock

- Select exact main connector.
- Select exact main fuse and holder.
- Select exact reverse-polarity MOSFET/controller.
- Select 5 V TVS device.
- Select host eFuse/load switch with reverse-current behavior.
- Decide servo branch grouping and connector count.
- Determine copper weight and calculate/verify voltage drop.
- Validate USB-C + HAT simultaneous-power behavior.

## 17. Exit criteria

Power design can move to REVIEW when:

- all exact protection parts are selected,
- input connector is frozen,
- servo branch topology is frozen,
- host protection part is frozen,
- current budget is linked and accepted,
- voltage-drop/copper calculations are complete,
- schematic ERC passes,
- PCB power-path review passes.

**Do not fabricate from this document alone.**
