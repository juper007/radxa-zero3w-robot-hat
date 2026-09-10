#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "sensors_v1_connectivity.csv"
rows = list(csv.DictReader(CSV.open(newline="", encoding="utf-8")))
index = {(r["RefDes"], r["Pin/Node"]): r for r in rows}
errors = []

def require(ref, pin, target):
    row = index.get((ref, pin))
    if row is None:
        errors.append(f"missing {ref}.{pin}")
        return
    if target not in row["Connects_To"]:
        errors.append(f"{ref}.{pin}: expected {target!r} in {row['Connects_To']!r}")

require("J40", "pin3", "I2C3_SDA")
require("J40", "pin5", "I2C3_SCL")
require("J40", "pin17", "+3V3")
require("R_I2C_SDA", "1", "+3V3")
require("R_I2C_SDA", "2", "I2C3_SDA")
require("R_I2C_SCL", "1", "+3V3")
require("R_I2C_SCL", "2", "I2C3_SCL")

for pin, target in (("pin1", "GND"), ("pin2", "+3V3"), ("pin3", "I2C3_SDA"), ("pin4", "I2C3_SCL")):
    require("J_QWIIC", pin, target)

require("J_IMU_DXL", "pin1", "GND")
require("J_IMU_DXL", "pin3", "DXL_DATA")

# The on-HAT BMI088 must remain optional for current MicroDuck compatibility.
for pin in ("VDD", "GND", "SDA", "SCL"):
    row = index.get(("U_BMI088", pin))
    if row is None or row.get("Status") != "DNP_OPTIONAL":
        errors.append(f"U_BMI088.{pin} must remain DNP_OPTIONAL in V1")

if errors:
    print("SENSOR DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

pending = [r for r in rows if r["Status"] in {"PROVISIONAL", "DNP_OPTIONAL"}]
print("SENSOR DESIGN CHECK: PASS (architecture invariants)")
print(f"Validated {len(rows)} rows; {len(pending)} rows remain optional/provisional")
