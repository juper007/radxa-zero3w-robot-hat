#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent / "libraries" / "RadxaRobotHat.pretty"
RPW = ROOT / "TI_RPW0010A_2x2mm_P0.45mm.kicad_mod"
text = RPW.read_text(encoding="utf-8")
errors = []

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
        errors.append(f"{token}: expected {count} copper shapes, got {got}")

# TI 4225183/A HotRod critical geometry.
checks = [
    '(at -0.25 0) (size 0.3 2.4)',
    '(at 0.25 0) (size 0.3 2.4)',
    '(at -0.9 -0.225) (size 0.6 0.25)',
    '(at -0.9 0.225) (size 0.6 0.25)',
    '(at 0.9 -0.225) (size 0.6 0.25)',
    '(at 0.9 0.225) (size 0.6 0.25)',
    '(at -0.725 -0.875) (size 0.25 0.65)',
    '(at 0.725 0.875) (size 0.25 0.65)',
]
for c in checks:
    if c not in text:
        errors.append(f"missing critical RPW geometry: {c}")

if errors:
    print("FOOTPRINT CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("FOOTPRINT CHECK: PASS")
print("TI RPW0010A HotRod pad-count and critical-geometry invariants present")
