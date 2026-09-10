#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "dynamixel_v1_connectivity.csv"
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

require("J40", "pin8", "UART2_TX")
require("J40", "pin10", "UART2_RX")
require("J40", "pin17", "+3V3")
for u in ("U5", "U6", "U7"):
    require(u, "VCC", "+3V3")
    require(u, "GND", "GND")

# All V1 TTL branches must share one DATA net while retaining independent power rails.
for ref, rail in (("J_DXL_A", "+5V_SERVO_A"), ("J_DXL_B", "+5V_SERVO_B"), ("J_DXL_C", "+5V_SERVO_C")):
    require(ref, "pin1", "GND")
    require(ref, "pin2", rail)
    require(ref, "pin3", "DXL_DATA")

require("J_IMU_DXL", "pin1", "GND")
require("J_IMU_DXL", "pin3", "DXL_DATA")
require("TP_DXL", "", "DXL_DATA")

# V1 must not accidentally make RS-485 mandatory.
row = index.get(("U8", "all"))
if row is None or row.get("Status") != "DNP":
    errors.append("U8 RS-485 path must remain DNP for core XL330 V1")

if errors:
    print("DYNAMIXEL DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

recovering = [r for r in rows if r["Status"] in {"RECOVERING", "TO_VERIFY", "PROVISIONAL", "SELECTING"}]
print("DYNAMIXEL DESIGN CHECK: PASS (connectivity invariants)")
print(f"Validated {len(rows)} rows; {len(recovering)} rows still require design freeze/review")
