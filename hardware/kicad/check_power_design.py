#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "power_v1_connectivity.csv"

rows = list(csv.DictReader(CSV.open(newline="", encoding="utf-8")))
index = {(r["RefDes"], r["Pin/Node"]): r for r in rows}
errors = []

def require(ref, pin, target_contains):
    row = index.get((ref, pin))
    if row is None:
        errors.append(f"missing {ref}.{pin}")
        return
    if target_contains not in row["Connects_To"]:
        errors.append(f"{ref}.{pin}: expected connection containing {target_contains!r}, got {row['Connects_To']!r}")

# LM74700 ideal-diode topology: ANODE=input/source, CATHODE=output/drain.
require("U1", "ANODE", "F1_OUT")
require("U1", "CATHODE", "+5V_SYS")
require("Q1", "SOURCE", "F1_OUT")
require("Q1", "DRAIN", "+5V_SYS")
require("Q1", "GATE", "U1_GATE")

# TPS259470A RPW pin-function intent.
require("U2", "IN", "+5V_SYS")
require("U2", "OUT", "+5V_RADXA")
require("U2", "GND", "GND")
require("U2", "EN/UVLO", "R_EN")
require("U2", "OVLO", "R_OV_DIV")
require("U2", "ILM", "R_ILIM")
require("U2", "DVDT", "C_DVDT")

# Radxa 5V injection pins.
require("J40", "pin2", "+5V_RADXA")
require("J40", "pin4", "+5V_RADXA")

# Three independent nominal servo branches.
for ref, rail in [("J2", "+5V_SERVO_A"), ("J3", "+5V_SERVO_B"), ("J4", "+5V_SERVO_C")]:
    require(ref, "VCC", rail)
    require(ref, "GND", "GND")

# High-current branch split must be copper net ties, not generic zero-ohm resistors.
for ref, rail in [("NTA", "+5V_SERVO_A"), ("NTB", "+5V_SERVO_B"), ("NTC", "+5V_SERVO_C")]:
    require(ref, "pin1", "+5V_SYS")
    require(ref, "pin2", rail)

for stale_ref in ("RBA", "RBB", "RBC"):
    if any(r["RefDes"] == stale_ref for r in rows):
        errors.append(f"stale high-current zero-ohm branch link still present: {stale_ref}")

if errors:
    print("POWER DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("POWER DESIGN CHECK: PASS")
print(f"Validated {len(rows)} connectivity rows in {CSV.name}")
print("Servo branches use explicit high-current copper net ties NTA/NTB/NTC; generic 0-ohm links are rejected.")
