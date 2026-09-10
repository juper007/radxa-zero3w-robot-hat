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
    'L Device:R_Small R31',
    'L Device:R_Small R32',
    'F 1 "20k"', 'F 1 "150R"',
    'UART2_TX', 'UART2_RX', 'Dynamixel_dir', 'DXL_LOCAL', 'DXL_DATA',
    'TTL_RX_OUT', 'RS485_RX_BIAS', '+5V_SERVO_A', '+5V_SERVO_B', '+5V_SERVO_C',
    'J_DXL_A', 'J_DXL_B', 'J_DXL_C', 'J_IMU_DXL',
]
for token in required_tokens:
    if token not in text:
        errors.append(f"missing schematic token: {token}")

anchor_wires = [
    '\t3450 2300 3700 2300',   # UART2_TX -> U7.A pin2
    '\t4800 2300 4950 2300',   # U7.Y pin4 -> R33/local node
    '\t5150 2300 6800 2300',   # R33 -> external DXL_DATA trunk
    '\t4800 3300 5000 3300',   # U6.Y -> TTL_RX_OUT
    '\t5000 3400 5300 3400',   # TTL_RX_OUT -> U5 input
    '\t5350 3200 5300 3200',   # RS485 DNP-safe bias -> U5 second input
    '\t6400 3300 6600 3300',   # U5.Y -> UART2_RX
    '\t5000 3100 5000 3300',   # R31 pull-up -> TTL_RX_OUT
    '\t4900 2000 4900 2300',   # R32 pull-up -> DXL_LOCAL
]
for wire in anchor_wires:
    if wire not in text:
        errors.append(f"missing expected pin-anchor wire: {wire.strip()}")

# KiCad 74xGxx symbols use positive local Y downward in this legacy orientation.
# Therefore VCC (+10.16 mm local Y) appears 400 mil BELOW center, while GND (-10.16 mm)
# appears 400 mil ABOVE center. This counter-intuitive geometry is verified against
# the upstream Pollen KiCad symbol definitions.
correct_power = [
    'Text Label 4100 2700 1 50 ~ 0\n+3V3', # U7 VCC pin5
    'Text Label 4100 1900 3 50 ~ 0\nGND',   # U7 GND pin3
    'Text Label 4300 2700 1 50 ~ 0\nDynamixel_dir', # U7 OE pin1
    'Text Label 4100 3700 1 50 ~ 0\n+3V3', # U6 VCC pin5
    'Text Label 4100 2900 3 50 ~ 0\nGND',   # U6 GND pin3
    'Text Label 4300 3700 1 50 ~ 0\nDynamixel_dir', # U6 /OE pin1
    'Text Label 5900 3700 1 50 ~ 0\n+3V3', # U5 VCC pin5
    'Text Label 5900 2900 3 50 ~ 0\nGND',   # U5 GND pin3
]
for token in correct_power:
    if token not in text:
        errors.append(f"missing verified logic power/OE anchor pattern: {token.splitlines()[0]}")

# R31 and R32 are both 10k in the upstream BOM and schematic.
if text.count('F 1 "10k"') < 5:
    errors.append('expected at least five 10k resistors including R26/R27/R31/R32/R34')

if text.count('$Comp') < 18:
    errors.append(f"expected at least 18 populated schematic components, found {text.count('$Comp')}")
if not text.rstrip().endswith('$EndSCHEMATC'):
    errors.append('legacy schematic terminator missing')

if errors:
    print('DYNAMIXEL IMPORT SCHEMATIC CHECK: FAIL')
    for err in errors:
        print(' -', err)
    raise SystemExit(1)

print('DYNAMIXEL IMPORT SCHEMATIC CHECK: PASS')
print('Verified VCC/GND/OE anchors plus upstream R31 RX pull-up and R32 DXL_LOCAL pull-up.')
print('NOTE: structure/connectivity guard only; KiCad 9 import/save/ERC/DRC is still required before fabrication.')
