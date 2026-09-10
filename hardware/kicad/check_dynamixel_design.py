#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "dynamixel_v1_connectivity.csv"
rows = list(csv.DictReader(CSV.open(newline="", encoding="utf-8")))
index = {(r["RefDes"], r["Pin/Node"]): r for r in rows}
errors = []

def require(ref, pin, target, status=None):
    row = index.get((ref, pin))
    if row is None:
        errors.append(f"missing {ref}.{pin}")
        return
    if target not in row["Connects_To"]:
        errors.append(f"{ref}.{pin}: expected {target!r} in {row['Connects_To']!r}")
    if status is not None and row.get("Status") != status:
        errors.append(f"{ref}.{pin}: expected status {status!r}, got {row.get('Status')!r}")

require("J40", "pin8", "UART2_TX")
require("J40", "pin10", "UART2_RX")
require("J40", "pin17", "+3V3")
for u in ("U5", "U6", "U7"):
    require(u, "VCC", "+3V3")
    require(u, "GND", "GND")

require("U7", "A", "UART2_TX")
require("U7", "Y", "DXL_LOCAL")
require("U6", "A", "DXL_LOCAL")
require("U6", "Y", "TTL_RX_OUT")
require("U5", "A", "TTL_RX_OUT")
require("U5", "Y", "UART2_RX")

# Restored upstream pull-ups that are required for deterministic half-duplex behavior.
require("R31", "pin1", "+3V3", "UPSTREAM_VERIFIED")
require("R31", "pin2", "TTL_RX_OUT", "UPSTREAM_VERIFIED")
require("R32", "pin1", "+3V3", "UPSTREAM_VERIFIED")
require("R32", "pin2", "DXL_LOCAL", "UPSTREAM_VERIFIED")

# TTL-only V1 policy: U8 RS485 is DNP, so the unused U5 input is forced high.
require("U5", "B", "RS485_RX_IDLE_HIGH", "V1_FROZEN")
require("R_RS485_IDLE", "pin1", "+3V3", "V1_FROZEN")
require("R_RS485_IDLE", "pin2", "RS485_RX_IDLE_HIGH", "V1_FROZEN")

require("U6", "OE", "Dynamixel_dir", "UPSTREAM_VERIFIED")
require("U7", "OE", "Dynamixel_dir", "UPSTREAM_VERIFIED")
require("DIR", "LOW", "U7_DISABLED/U6_ENABLED", "UPSTREAM_VERIFIED")
require("DIR", "HIGH", "U7_ENABLED/U6_DISABLED", "UPSTREAM_VERIFIED")

require("R26", "top", "+3V3", "UPSTREAM_VERIFIED")
require("R26", "bottom", "UART2_TX_DIR_SENSE", "UPSTREAM_VERIFIED")
require("R27", "pin1", "UART2_TX_DIR_SENSE", "UPSTREAM_VERIFIED")
require("R27", "pin2", "Q1_BASE", "UPSTREAM_VERIFIED")
require("Q1", "pin1_BASE", "Q1_BASE", "UPSTREAM_VERIFIED")
require("Q1", "pin2_EMITTER", "+3V3", "UPSTREAM_VERIFIED")
require("Q1", "pin3_COLLECTOR", "Dynamixel_dir", "UPSTREAM_VERIFIED")
require("R28", "top", "Dynamixel_dir", "UPSTREAM_VERIFIED")
require("R28", "bottom", "GND", "UPSTREAM_VERIFIED")
require("DIRGEN", "UART2_TX_IDLE_HIGH", "Dynamixel_dir_LOW", "UPSTREAM_VERIFIED")
require("DIRGEN", "UART2_TX_LOW", "Dynamixel_dir_HIGH", "UPSTREAM_VERIFIED")

require("R33", "pin1", "DXL_LOCAL", "UPSTREAM_VERIFIED")
require("R33", "pin2", "DXL_DATA", "UPSTREAM_VERIFIED")

for ref, rail in (("J_DXL_A", "+5V_SERVO_A"), ("J_DXL_B", "+5V_SERVO_B"), ("J_DXL_C", "+5V_SERVO_C")):
    require(ref, "pin1", "GND")
    require(ref, "pin2", rail)
    require(ref, "pin3", "DXL_DATA")

require("J_IMU_DXL", "pin1", "GND")
require("J_IMU_DXL", "pin3", "DXL_DATA")
require("TP_DXL", "", "DXL_DATA")

row = index.get(("U8", "all"))
if row is None or row.get("Status") != "DNP":
    errors.append("U8 RS-485 path must remain DNP for core XL330 V1")

if errors:
    print("DYNAMIXEL DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

open_items = [r for r in rows if r["Status"] in {"RECOVERING", "TO_VERIFY", "PROVISIONAL", "SELECTING"}]
print("DYNAMIXEL DESIGN CHECK: PASS (connectivity invariants)")
print(f"Validated {len(rows)} rows; {len(open_items)} rows still require design freeze/review")
