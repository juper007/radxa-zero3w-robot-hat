#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "libraries" / "RadxaRobotHat.pretty"
RPW = ROOT / "TI_RPW0010A_2x2mm_P0.45mm.kicad_mod"
BSC = ROOT / "Infineon_PG-TDSON-8_SuperSO8.kicad_mod"
errors = []

# TPS259470A RPW HotRod invariants
text = RPW.read_text(encoding="utf-8")
required = {
    'pad "1"': 2,
    'pad "2"': 1,
    'pad "3"': 1,
    'pad "4"': 2,
    'pad "5"': 1,
    'pad "6"': 1,
    'pad "7"': 2,
    'pad "8"': 1,
    'pad "9"': 1,
    'pad "10"': 2,
}
for token, count in required.items():
    got = text.count(f"({token}")
    if got != count:
        errors.append(f"RPW {token}: expected {count} copper shapes, got {got}")

for c in [
    '(at -0.25 0) (size 0.3 2.4)',
    '(at 0.25 0) (size 0.3 2.4)',
    '(at -0.9 -0.225) (size 0.6 0.25)',
    '(at -0.9 0.225) (size 0.6 0.25)',
    '(at 0.9 -0.225) (size 0.6 0.25)',
    '(at 0.9 0.225) (size 0.6 0.25)',
    '(at -0.725 -0.875) (size 0.25 0.65)',
    '(at 0.725 0.875) (size 0.25 0.65)',
]:
    if c not in text:
        errors.append(f"missing critical RPW geometry: {c}")

# BSC009 / Infineon PG-TDSON-8 SuperSO8 invariants.
# Geometry follows Infineon recommended boardpads and is cross-checked against
# KiCad's TDSON-8-1 reference footprint. Pins 1-3 source, 4 gate, 5-8 drain.
b = BSC.read_text(encoding="utf-8")
for p in ('"1"', '"2"', '"3"', '"4"', '"5"', '"6"', '"7"', '"8"'):
    if f'(pad {p}' not in b:
        errors.append(f"BSC missing electrical pad {p}")

bsc_checks = [
    '(at -2.90 -1.905) (size 0.85 0.50)',
    '(at -2.90 -0.635) (size 0.85 0.50)',
    '(at -2.90 0.635) (size 0.85 0.50)',
    '(at -2.90 1.905) (size 0.85 0.50)',
    '(at 1.05 0) (size 4.55 4.41)',
    '(at 2.905 -1.905) (size 0.80 0.60)',
    '(at 2.905 -0.635) (size 0.80 0.60)',
    '(at 2.905 0.635) (size 0.80 0.60)',
    '(at 2.905 1.905) (size 0.80 0.60)',
    '(at -0.20 -0.85) (size 1.50 1.50)',
    '(at 1.50 0.85) (size 1.50 1.50)',
]
for c in bsc_checks:
    if c not in b:
        errors.append(f"missing critical BSC009 geometry: {c}")

if errors:
    print("FOOTPRINT CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("FOOTPRINT CHECK: PASS")
print("TPS259470A RPW and BSC009 PG-TDSON-8/SuperSO8 critical geometry invariants present")
