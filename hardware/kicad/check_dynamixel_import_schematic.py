#!/usr/bin/env python3
from pathlib import Path

SCH = Path(__file__).resolve().parent / "dynamixel_v17_import.sch"
text = SCH.read_text(encoding="utf-8")
errors = []

required_tokens = [
    'L 74xGxx:74LVC1G126 U7',
    'L 74xGxx:74LVC1G125 U6',
    'L 74xGxx:74LVC1G08 U5',
    'L Transistor_BJT:MMBT3906 Q1',
    'F 1 "10k"', 'F 1 "20k"', 'F 1 "150R"',
    'UART2_TX', 'UART2_RX', 'Dynamixel_dir', 'DXL_LOCAL', 'DXL_DATA',
    'TTL_RX_OUT', 'RS485_RX_BIAS', '+5V_SERVO_A', '+5V_SERVO_B', '+5V_SERVO_C',
    'J_DXL_A', 'J_DXL_B', 'J_DXL_C', 'J_IMU_DXL',
]
for token in required_tokens:
    if token not in text:
        errors.append(f"missing schematic token: {token}")

# Signal pin anchors based on KiCad 74xGxx library definitions.
anchor_wires = [
    '\t3450 2300 3700 2300',   # UART2_TX -> U7.A (pin 2)
    '\t4800 2300 4950 2300',   # U7.Y (pin 4) -> R33
    '\t5150 2300 5400 2300',   # R33 -> DXL_DATA
    '\t3450 3300 3700 3300',   # DXL_LOCAL -> U6.A (pin 2)
    '\t4800 3300 5000 3300',   # U6.Y (pin 4) -> receive path
    '\t5000 3400 5300 3400',   # TTL_RX_OUT -> U5 input
    '\t5350 3200 5300 3200',   # RS485 idle-high bias -> U5 second input
    '\t6400 3300 6600 3300',   # U5.Y -> UART2_RX
]
for wire in anchor_wires:
    if wire not in text:
        errors.append(f"missing expected pin-anchor wire: {wire.strip()}")

# Critical correction from validation review: +3V3 is on the upper VCC anchors,
# GND on the lower anchors, and OE is on the upper center anchor for 1G125/126.
correct_labels = [
    'Text Label 4100 1900', # U7 VCC pin 5
    'Text Label 4300 1900', # U7 OE pin 1 (active high)
    'Text Label 4100 2700', # U7 GND pin 3
    'Text Label 4100 2900', # U6 VCC pin 5
    'Text Label 4300 2900', # U6 /OE pin 1 (active low)
    'Text Label 4100 3700', # U6 GND pin 3
    'Text Label 5900 2900', # U5 VCC pin 5
    'Text Label 5900 3700', # U5 GND pin 3
]
for token in correct_labels:
    if token not in text:
        errors.append(f"missing corrected logic power/OE anchor: {token}")

# Explicitly reject the v0.15 inverted power-anchor pattern.
wrong_pairs = [
    'Text Label 4100 2700 1 50 ~ 0\n+3V3',
    'Text Label 4100 1900 3 50 ~ 0\nGND',
    'Text Label 4100 3700 1 50 ~ 0\n+3V3',
    'Text Label 4100 2900 3 50 ~ 0\nGND',
    'Text Label 5900 3700 1 50 ~ 0\n+3V3',
    'Text Label 5900 2900 3 50 ~ 0\nGND',
]
for bad in wrong_pairs:
    if bad in text:
        errors.append('regression: inverted U5/U6/U7 logic power anchor pattern detected')

if text.count('$Comp') < 16:
    errors.append(f"expected at least 16 populated schematic components, found {text.count('$Comp')}")
if not text.rstrip().endswith('$EndSCHEMATC'):
    errors.append('legacy schematic terminator missing')

if errors:
    print('DYNAMIXEL IMPORT SCHEMATIC CHECK: FAIL')
    for err in errors:
        print(' -', err)
    raise SystemExit(1)

print('DYNAMIXEL IMPORT SCHEMATIC CHECK: PASS')
print('Validation-corrected import draft contains required devices/nets and corrected VCC/GND/OE anchors.')
print('NOTE: structure/connectivity guard only; KiCad 9 import/save/ERC/DRC is still required before fabrication.')
