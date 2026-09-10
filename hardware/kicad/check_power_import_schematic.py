#!/usr/bin/env python3
from pathlib import Path

SCH = Path(__file__).resolve().parent / "power_v16_import.sch"
text = SCH.read_text(encoding="utf-8")
errors = []

required = [
    'RadxaRobotHatPower:LM74700QDBVRQ1 U1',
    'RadxaRobotHatPower:BSC009NE2LS5I Q1',
    'RadxaRobotHatPower:TPS259470ARPWR U2',
    'Connector_Generic:Conn_01x02 J1',
    'Connector_Generic:Conn_01x03 J40_PWR',
    'F 1 "20A"',
    'F 1 "390k"',
    'F 1 "374k"',
    'F 1 "100k"',
    'F 1 "825R"',
    'F 1 "3.9n"',
    'F1_IN', 'F1_OUT', '+5V_SYS', '+5V_RADXA',
    '+5V_SERVO_A', '+5V_SERVO_B', '+5V_SERVO_C',
    'Q1_GATE', 'U1_VCAP', 'U2_EN', 'U2_OVLO', 'U2_ILM', 'U2_DVDT',
]
for token in required:
    if token not in text:
        errors.append(f"missing schematic token: {token}")

# Critical custom-symbol anchor labels, derived from the project-local symbol definitions.
anchors = [
    'Text Label 3100 2000', # U1 ANODE
    'Text Label 3900 2000', # U1 CATHODE
    'Text Label 3900 2150', # U1 GATE
    'Text Label 3500 2350', # U1 VCAP
    'Text Label 3500 1650', # U1 GND
    'Text Label 4600 1900', # Q1 source 3
    'Text Label 4600 2000', # Q1 source 2
    'Text Label 4600 2100', # Q1 source 1
    'Text Label 5000 1700', # Q1 gate
    'Text Label 5400 1850', # Q1 drain 5
    'Text Label 5400 2150', # Q1 drain 8
    'Text Label 6550 2600', # U2 IN
    'Text Label 7450 2600', # U2 OUT
    'Text Label 6550 2900', # U2 EN
    'Text Label 6550 2750', # U2 OVLO
    'Text Label 7450 2450', # U2 DVDT
    'Text Label 6550 2450', # U2 ILM
    'Text Label 7000 2100', # U2 GND
]
for token in anchors:
    if token not in text:
        errors.append(f"missing custom-symbol anchor: {token}")

# Generic connector endpoint regression: single-row connector pins are 200 mil left of center.
for token in ['Text Label 1000 1950', 'Text Label 1000 2050',
              'Text Label 8000 4150', 'Text Label 8000 4250',
              'Text Label 8000 4650', 'Text Label 8000 4750',
              'Text Label 8000 5150', 'Text Label 8000 5250']:
    if token not in text:
        errors.append(f"missing connector pin anchor: {token}")

if text.count('$Comp') < 33:
    errors.append(f"expected at least 33 populated components/interfaces, found {text.count('$Comp')}")
if not text.rstrip().endswith('$EndSCHEMATC'):
    errors.append('legacy schematic terminator missing')

# Prevent regression to the discarded wide-input/buck architecture.
for forbidden in ['5-28V input', 'AP63205', 'onboard high-power buck']:
    if forbidden in text:
        errors.append(f"forbidden stale V1 architecture token present: {forbidden}")

if errors:
    print('POWER IMPORT SCHEMATIC CHECK: FAIL')
    for err in errors:
        print(' -', err)
    raise SystemExit(1)

print('POWER IMPORT SCHEMATIC CHECK: PASS')
print('Populated power import draft contains the frozen ideal-diode, host eFuse, servo rails and checked pin anchors.')
print('NOTE: structure/connectivity guard only; KiCad 9 import/save/ERC/DRC is still required before fabrication.')
