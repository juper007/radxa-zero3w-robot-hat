#!/usr/bin/env python3
from pathlib import Path

SCH = Path(__file__).resolve().parent / "dynamixel_v15_import.sch"
text = SCH.read_text(encoding="utf-8")
errors = []

required_tokens = [
    'L 74xGxx:74LVC1G126 U7',
    'L 74xGxx:74LVC1G125 U6',
    'L 74xGxx:74LVC1G08 U5',
    'L Transistor_BJT:MMBT3906 Q1',
    'F 1 "10k"',
    'F 1 "20k"',
    'F 1 "150R"',
    'UART2_TX',
    'UART2_RX',
    'Dynamixel_dir',
    'DXL_LOCAL',
    'DXL_DATA',
    'TTL_RX_OUT',
    'RS485_RX_BIAS',
    '+5V_SERVO_A',
    '+5V_SERVO_B',
    '+5V_SERVO_C',
    'J_DXL_A',
    'J_DXL_B',
    'J_DXL_C',
    'J_IMU_DXL',
]
for token in required_tokens:
    if token not in text:
        errors.append(f"missing schematic token: {token}")

# Pin-anchor regression checks based on the KiCad standard symbol definitions
# used by the imported legacy schematic. These are structure guards, not ERC.
anchor_wires = [
    '\t3450 2300 3700 2300',   # UART2_TX -> U7.A
    '\t4800 2300 4950 2300',   # U7.Y -> R33 input
    '\t3700 3300 3450 3300',   # U6.A on DXL_LOCAL
    '\t4800 3300 5000 3300',   # U6.Y -> TTL_RX_OUT route
    '\t5000 3400 5300 3400',   # TTL_RX_OUT -> U5 input A
    '\t6400 3300 6600 3300',   # U5.Y -> UART2_RX
    '\t5350 3200 5300 3200',   # RS485 idle-high bias -> U5 input B
]
for wire in anchor_wires:
    if wire not in text:
        errors.append(f"missing expected pin-anchor wire: {wire.strip()}")

power_labels = [
    'Text Label 4100 2700', # U7 VCC
    'Text Label 4100 1900', # U7 GND
    'Text Label 4100 3700', # U6 VCC
    'Text Label 4100 2900', # U6 GND
    'Text Label 5900 3700', # U5 VCC
    'Text Label 5900 2900', # U5 GND
]
for token in power_labels:
    if token not in text:
        errors.append(f"missing logic power anchor: {token}")

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
print('Populated legacy KiCad import draft contains required devices, nets, connectors and checked pin-anchor routes.')
print('NOTE: this is not KiCad ERC; KiCad 9 import/save/ERC is still required before fabrication.')
