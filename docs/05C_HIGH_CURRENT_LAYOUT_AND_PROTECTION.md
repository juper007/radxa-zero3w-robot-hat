# High-Current Layout and Main Protection — V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × XL330-M288-T  
Last updated: 2026-09-09

## 1. Scope

This document freezes the first practical high-current power-path design for the V1 board.

The board uses a regulated external 5 V supply. The main HAT PCB does **not** convert a higher battery voltage down to the 20 A-class servo rail.

## 2. Main protection architecture

Selected candidate architecture:

```text
5V INPUT
  |
 [F1]
  |
 [LM74700-Q1 + external N-MOSFET]
  |
 +5V_SYS
  |------------------> Servo power branches
  |
  +--> TPS25947 host eFuse --> +5V_RADXA
```

### Main ideal-diode controller

**TI LM74700-Q1**

Reasons:
- 3.2 V to 65 V operating input range
- external N-channel MOSFET gate drive
- reverse-polarity protection
- reverse-current blocking
- approximately 20 mV forward-drop regulation
- fast reverse-current response
- small package

This device is used for the **main input path**, not the Radxa-only branch.

### Main MOSFET

**Infineon BSC009NE2LS5I**

Key design data:
- 25 V VDS rating
- SuperSO8 / 5 × 6 mm power package
- max RDS(on) approximately 1.35 mΩ at VGS = 4.5 V
- very large pulse/current capability when PCB thermals are adequate

At 20 A, using 1.35 mΩ as a conservative conduction estimate:

- Voltage drop ≈ 27 mV
- Conduction loss ≈ 0.54 W

This is acceptable only with a proper copper thermal area. Connector and PCB copper loss can be larger than MOSFET loss, so layout dominates.

## 3. Connector decision

### V1 prototype: XT60-class input

**Decision: use XT60-class external input for V1 prototype/bring-up.**

Reason:
- The 15-servo theoretical stall envelope exceeds 20 A.
- XT30 is mechanically attractive but has too little comfortable margin for repeated high-current bench testing.
- V1 should prioritize electrical margin over minimum volume.

Mechanical implementation options:
1. board-mounted XT60 if enclosure clearance allows,
2. large solder pads + short XT60 pigtail if board-mounted connector is too large,
3. alternate high-current locking connector in later mechanical revision.

XT30 may be reconsidered only after measured locomotion current shows enough margin.

## 4. PCB copper strategy

### 4.1 Copper weight

V1 target: **2 oz outer-layer copper preferred** for prototype fabrication.

If the fab stack limits inner copper to 1 oz, use outer-layer high-current pours and dense via stitching to share current where practical.

### 4.2 DC copper-loss model

For first-order comparison, copper resistance is approximated by:

`R = rho * L / (W * t)`

Assumptions:
- copper resistivity: 1.724e-8 Ω·m
- representative path length: 30 mm
- 1 oz copper thickness ≈ 35 µm
- 2 oz copper thickness ≈ 70 µm

This is a **loss estimate**, not an IPC thermal-rise certification.

### 4.3 30 mm path, 1 oz copper

| Width | Resistance | Loss @10A | Loss @15A | Loss @20A |
|---:|---:|---:|---:|---:|
| 5 mm | 2.96 mΩ | 0.30 W | 0.66 W | 1.18 W |
| 8 mm | 1.85 mΩ | 0.18 W | 0.42 W | 0.74 W |
| 10 mm | 1.48 mΩ | 0.15 W | 0.33 W | 0.59 W |
| 15 mm | 0.99 mΩ | 0.10 W | 0.22 W | 0.39 W |
| 20 mm | 0.74 mΩ | 0.07 W | 0.17 W | 0.30 W |

### 4.4 30 mm path, 2 oz copper

| Width | Resistance | Loss @10A | Loss @15A | Loss @20A |
|---:|---:|---:|---:|---:|
| 5 mm | 1.48 mΩ | 0.15 W | 0.33 W | 0.59 W |
| 8 mm | 0.92 mΩ | 0.09 W | 0.21 W | 0.37 W |
| 10 mm | 0.74 mΩ | 0.07 W | 0.17 W | 0.30 W |
| 15 mm | 0.49 mΩ | 0.05 W | 0.11 W | 0.20 W |
| 20 mm | 0.37 mΩ | 0.04 W | 0.08 W | 0.15 W |

## 5. Routing rules derived from the loss model

For the input-to-distribution trunk:
- do not use ordinary traces,
- use polygon pours,
- target an **effective width >= 15 mm equivalent on 2 oz copper** wherever the full current is carried,
- parallel top and bottom copper when possible,
- connect layers with dense arrays of large vias,
- minimize path length from connector -> fuse -> MOSFET -> branch split.

For branch paths:
- split servo loads physically close to the main protection stage,
- avoid routing the entire servo current through one narrow neck,
- put local bulk capacitors at each branch connector/group.

## 6. Servo branch topology

Initial grouping:

```text
+5V_SYS
  +--> SERVO_A  (up to 5 servos)
  +--> SERVO_B  (up to 5 servos)
  +--> SERVO_C  (up to 5 servos)
  +--> HOST_EFUSE --> +5V_RADXA
```

The grouping is electrical/load-distribution guidance; the exact robot harness mapping can change later.

Theoretical stall per 5-servo branch:
- 5 × 1.47 A = 7.35 A

Therefore each branch connector/copper path should tolerate short high-current events above 7 A, even though normal average current should be much lower.

## 7. Fuse strategy

The fuse protects wiring and PCB from sustained faults; it is not intended to permit simultaneous servo stall indefinitely.

Prototype recommendation:
- external or replaceable **20 A class fuse** in the main input path,
- final value must be matched to PSU limit, connector, wire gauge, PCB thermal tests and actual robot current waveforms.

A 15 A fuse remains an alternate if locomotion testing shows lower peaks and nuisance trips are acceptable.

## 8. Host branch protection

Use **TPS25947 family** only on the Radxa branch.

Target host allocation:
- Radxa official recommendation: >=15 W at 5 V
- baseline required current: >=3 A
- design target: approximately 4 A normal protection threshold with transient headroom

The selected eFuse supports current limiting and true reverse-current blocking and is therefore suitable for separating HAT 5 V from possible USB-C sourced 5 V.

Exact suffix and ILIM resistor will be frozen after the TI current-limit equation is checked against the chosen fault mode.

## 9. Ground current strategy

The GND return must be treated with the same current importance as +5V.

Rules:
- high-current servo return goes directly to the input/bulk region,
- do not force servo return through the Radxa/header ground neck,
- use a continuous ground plane,
- add top/bottom ground copper around high-current connectors,
- use many stitching vias,
- keep codec/microphone analog region away from the high-current return corridor.

## 10. Thermal checkpoints

Prototype must measure:
- MOSFET case/top temperature,
- fuse temperature,
- XT60/pigtail joint temperature,
- input copper hot spots,
- branch connector hot spots,
- TPS25947 temperature at sustained 3 A / 4 A load.

## 11. Design lock for schematic drawing

The following are now sufficiently frozen for the schematic draft:

| Item | V1 choice |
|---|---|
| Input supply | regulated 5 V |
| Development PSU | 5 V / 15–20 A class |
| Input connector | XT60-class / pigtail-compatible |
| Main reverse protection controller | LM74700-Q1 |
| Main external MOSFET | BSC009NE2LS5I |
| Main fuse | 20 A class provisional |
| Servo branches | 3 groups × 5 servos nominal |
| Host eFuse | TPS25947 family |
| PCB copper | 2 oz outer preferred |
| Full-current routing | polygon pours, multi-layer sharing |

## 12. Remaining before fabrication

- Verify exact XT60 footprint/pigtail geometry.
- Select fuse holder/package.
- Freeze TPS25947 ordering suffix and programming network.
- Perform ERC on the actual KiCad schematic.
- Calculate/check current density and temperature rise using the selected PCB stackup.
- Review the 5 V input transient strategy because XL330 maximum operating voltage leaves limited overvoltage margin.

**Status remains DESIGNING. Not fabrication-ready.**
