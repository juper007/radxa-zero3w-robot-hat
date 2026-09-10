# Power Current Budget — MicroDuck V1

Status: DESIGNING  
Target: Radxa ZERO 3W + 15 × DYNAMIXEL XL330-M288-T  
Last updated: 2026-09-09

## 1. Why the architecture changed

The initial architecture retained the upstream Robot HAT's broad 5–28 V motor-input concept. That is useful for a generic robot HAT, but it is not the best fit for this project's actual actuator set.

The MicroDuck V1 target uses 15 × XL330-M288-T servos. XL330-M288-T is a low-voltage actuator with 3.7–6.0 V operating range and 5.0 V recommended input. At 5 V its published stall current is approximately 1.47 A per actuator.

The Radxa ZERO 3W also requires a 5 V supply.

Therefore the V1 design will use a **5 V high-current system bus** instead of converting a 12–28 V motor bus down to 5 V on the HAT.

## 2. Servo current budget

Published XL330-M288-T values at 5 V:

- Standby current: approximately 17 mA
- Stall current: approximately 1.47 A
- Recommended voltage: 5.0 V

For 15 servos:

| Condition | Per servo | 15 servos |
|---|---:|---:|
| Standby | 0.017 A | 0.255 A |
| 10% of stall-equivalent electrical load | 0.147 A | 2.205 A |
| 20% | 0.294 A | 4.410 A |
| 30% | 0.441 A | 6.615 A |
| 50% | 0.735 A | 11.025 A |
| Theoretical simultaneous stall | 1.47 A | 22.05 A |

The simultaneous-stall number is not a normal operating point, but it is useful for sizing fault tolerance, wiring, connector strategy, bulk capacitance and supply headroom.

## 3. Radxa and logic budget

Reserve the following preliminary envelope:

- Radxa ZERO 3W: 3 A design allocation at 5 V
- Audio codec/amplifier/microphone: 0.5 A provisional
- Logic, IMU, I2C peripherals: 0.25 A provisional
- Miscellaneous margin: 0.25 A

Non-servo allocation: **4.0 A provisional maximum design envelope**.

This does not imply the SBC continuously consumes 4 A. It is intentionally conservative for rail and connector design.

## 4. System current scenarios

| Scenario | Servo allocation | Host/logic | Total |
|---|---:|---:|---:|
| Idle | 0.255 A | 1–2 A typical envelope | ~1.3–2.3 A |
| Light motion | 2.2 A | 2 A | ~4.2 A |
| Moderate motion | 4.4–6.6 A | 2–3 A | ~6.4–9.6 A |
| Heavy transient | 11 A | 3 A | ~14 A |
| Simultaneous servo stall + host envelope | 22.05 A | 4 A | ~26 A |

## 5. V1 supply target

Recommended prototype supply class:

- Output: regulated 5.0 V
- Continuous capability: **>=15 A preferred for normal development**
- Better bench/robot margin: **20 A class**
- Short transient capability: as high as practical
- Current limiting and short-circuit protection required

A 25–30 A supply is not required for normal walking, but may be useful for worst-case validation. The robot firmware should prevent sustained simultaneous stall conditions.

## 6. HAT power architecture

```text
External regulated 5 V high-current supply
                 |
                 +--> Fuse / reverse-polarity protection
                 |
                 +--> +5V_SERVO_BUS --> distributed XL330 connectors
                 |
                 +--> protected host branch --> +5V_RADXA --> header pins 2,4
                 |
                 +--> filtered peripheral branches --> audio / logic
```

Key consequence: **No high-power 24 V → 5 V converter is required on V1.**

This reduces heat, EMI, cost and PCB area.

## 7. Current distribution rule

Do not route the full theoretical 20+ A servo current through a single narrow PCB trace or through a connector that was intended only for SBC power.

Preferred options:

1. High-current 5 V input enters close to servo power distribution.
2. Use wide copper pours on multiple layers with via stitching.
3. Split servo output connectors into branches.
4. Consider 2–3 separately fused servo power groups if layout allows.
5. Host 5 V branch gets independent protection/filtering.

## 8. Connector target

The main input connector should be selected for realistic robot current, not the theoretical current label alone.

Prototype target:

- >=15 A continuous connector rating
- Prefer >=20 A family if mechanically practical
- Polarized/keyed
- Low contact resistance
- Wire gauge compatible with expected current

Potential families to evaluate:

- XT30 class for compact moderate-current input
- XT60 class if maximum margin is prioritized
- High-current pluggable terminal block if serviceability is more important than size

The final connector will be chosen after mechanical fit review.

## 9. Fuse strategy

A single 25–30 A board fuse is not necessarily the best protection for thin servo wiring.

Preferred V1 strategy:

- Main input fuse sized to protect board/input wiring.
- Optional branch fuses or resettable protection for servo groups.
- Host branch protected separately in the 3–5 A class.

Exact values remain subject to connector/wire selection and measured robot motion current.

## 10. Voltage-drop budget

At 5 V, voltage drop matters significantly.

Target at high dynamic load:

- Supply connector + board distribution + cable drop should ideally stay below 0.25 V total.
- Radxa rail should remain within valid 5 V input range under transients.
- Servo bus should remain comfortably above XL330 low-voltage limits.

Because power is only 5 V, connector/contact resistance and PCB copper resistance must be treated as first-class design parameters.

## 11. Firmware dependency

Electrical design alone should not assume all 15 servos may remain stalled.

Firmware should implement:

- current/torque limits,
- thermal monitoring,
- supply-voltage monitoring,
- motion profiles that avoid synchronized current spikes,
- fault shutdown where practical.

## 12. Design decision

**V1 DECISION: use regulated 5 V external robot power as the primary input.**

The previous 5–28 V generic input goal is moved to a possible later universal-HAT revision.

This decision is specifically optimized for Radxa ZERO 3W + XL330-M288-T MicroDuck hardware.
