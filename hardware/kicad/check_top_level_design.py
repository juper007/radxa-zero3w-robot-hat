#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "top_level_v1_connectivity.csv"
rows = list(csv.DictReader(CSV.open(newline="", encoding="utf-8")))
errors = []

required = {
    "+5V_IN": ("J1", "F1"),
    "+5V_SYS": ("Q1_DRAIN/U1_CATHODE", "Servo_A/Servo_B/Servo_C/U2/U_AMP"),
    "+5V_RADXA": ("U2_OUT", "J40_pin2/J40_pin4"),
    "+3V3": ("J40_pin1/J40_pin17", "Logic/I2C/Audio"),
    "UART2_TX": ("J40_pin8", "U7_TX_BUFFER"),
    "UART2_RX": ("U5_RX_COMBINER", "J40_pin10"),
    "DXL_DATA": ("U7_TX/U6_RX", "J_DXL_A/J_DXL_B/J_DXL_C/J_IMU_DXL"),
    "I2C3_SDA": ("J40_pin3", "U_AUDIO/J_QWIIC/U_BMI088_optional"),
    "I2C3_SCL": ("J40_pin5", "U_AUDIO/J_QWIIC/U_BMI088_optional"),
    "I2S3_BCLK": ("J40_pin12", "U_AUDIO"),
    "I2S3_LRCLK": ("J40_pin35", "U_AUDIO"),
    "I2S3_SDI": ("U_AUDIO", "J40_pin38"),
    "I2S3_SDO": ("J40_pin40", "U_AUDIO"),
}

by_signal = {r["Signal"]: r for r in rows}
for signal, (src, dst) in required.items():
    row = by_signal.get(signal)
    if row is None:
        errors.append(f"missing top-level signal {signal}")
        continue
    if src not in row["Source"]:
        errors.append(f"{signal}: expected source containing {src!r}, got {row['Source']!r}")
    if dst not in row["Destination"]:
        errors.append(f"{signal}: expected destination containing {dst!r}, got {row['Destination']!r}")

if errors:
    print("TOP LEVEL DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("TOP LEVEL DESIGN CHECK: PASS (interface invariants)")
print(f"Validated {len(rows)} integration rows")
