#!/usr/bin/env python3
from pathlib import Path

SCH = Path(__file__).resolve().parent / "power_v17_import.sch"
text = SCH.read_text(encoding="utf-8")
errors = []

def require(token, desc=None):
    if token not in text:
        errors.append(f"missing {desc or token}: {token}")

# Core protection and host-power devices.
for token in [
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
]:
    require(token)

# Required named rails/control nets.
for net in [
    'F1_IN', 'F1_OUT', '+5V_SYS', '+5V_RADXA',
    '+5V_SERVO_A', '+5V_SERVO_B', '+5V_SERVO_C',
    'Q1_GATE', 'U1_VCAP', 'U2_EN', 'U2_OVLO', 'U2_ILM', 'U2_DVDT',
]:
    require(net, f"net {net}")

# High-current branch split: three explicit copper net ties, no resistor links.
for ref, rail in [('NTA', '+5V_SERVO_A'), ('NTB', '+5V_SERVO_B'), ('NTC', '+5V_SERVO_C')]:
    require(f'Device:Net-Tie_2 {ref}', f'{ref} net-tie symbol')
    require(f'F 1 "SERVO_{ref[-1]}_COPPER_TIE"' if ref[-1] in 'ABC' else '', f'{ref} value')
    require(rail, f'{ref} branch rail')

if text.count('RadxaRobotHat:HighCurrent_NetTie_2Pin_8mm') != 3:
    errors.append('expected exactly three HighCurrent_NetTie_2Pin_8mm footprint assignments')

# Each servo power connector and local branch bulk network must exist.
for token in [
    'Connector_Generic:Conn_01x02 J2', 'SERVO_A_PWR', 'CA1', 'CA2',
    'Connector_Generic:Conn_01x02 J3', 'SERVO_B_PWR', 'CB1', 'CB2',
    'Connector_Generic:Conn_01x02 J4', 'SERVO_C_PWR', 'CC1', 'CC2',
]:
    require(token)

# Critical power-device pin-label intent. These protect against source/drain or host-rail regressions.
for token in [
    'Text Label 3100 2000',  # LM74700 ANODE side = F1_OUT
    'Text Label 3900 2000',  # LM74700 CATHODE side = +5V_SYS
    'Text Label 4600 1900',  # BSC009 source bank
    'Text Label 5400 1850',  # BSC009 drain bank
    'Text Label 6550 2600',  # TPS25947 IN
    'Text Label 7450 2600',  # TPS25947 OUT
]:
    require(token)

# Reject known stale architectures and the unsafe branch-resistor implementation.
for forbidden in [
    '5-28V input', 'AP63205',
    'Device:R_Small RBA', 'Device:R_Small RBB', 'Device:R_Small RBC',
    'F 1 "0R"', 'F 1 "0 ohm"', 'F 1 "0ohm"',
]:
    if forbidden in text:
        errors.append(f"forbidden stale/unsafe V1 token present: {forbidden}")

require('no onboard high-power buck in V1')
require('no generic zero-ohm branch resistors')

if not text.rstrip().endswith('$EndSCHEMATC'):
    errors.append('legacy schematic terminator missing')

if errors:
    print('POWER IMPORT SCHEMATIC CHECK: FAIL')
    for err in errors:
        print(' -', err)
    raise SystemExit(1)

print('POWER IMPORT SCHEMATIC CHECK: PASS')
print('v0.17 draft contains the protected 5V path, TPS25947 host branch and three explicit high-current copper net ties.')
print('NOTE: this is an electrical-intent/structure regression guard; KiCad 9 import/save/ERC/DRC is still mandatory before fabrication.')
