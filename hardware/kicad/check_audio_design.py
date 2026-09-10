#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "audio_v1_connectivity.csv"
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

for pin, target in (("pin3", "I2C3_SDA"), ("pin5", "I2C3_SCL"), ("pin12", "I2S3_BCLK"), ("pin35", "I2S3_LRCLK"), ("pin38", "I2S3_SDI"), ("pin40", "I2S3_SDO")):
    require("J40", pin, target)

for pin, target in (("CTRL_SDA", "I2C3_SDA"), ("CTRL_SCL", "I2C3_SCL"), ("BCLK", "I2S3_BCLK"), ("WCLK", "I2S3_LRCLK"), ("DOUT", "I2S3_SDI"), ("DIN", "I2S3_SDO")):
    require("U_AUDIO", pin, target)

require("Y_AUDIO", "OUT", "CODEC_MCLK")
require("U_AUDIO", "MCLK", "CODEC_MCLK")
require("U_AMP", "VCC", "+5V_SYS")
require("J_SPK", "OUT", "U_AMP_BTL_OUT")

if errors:
    print("AUDIO DESIGN CHECK: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

pending = [r for r in rows if r["Status"] in {"RECOVERING", "PROVISIONAL"}]
print("AUDIO DESIGN CHECK: PASS (architecture invariants)")
print(f"Validated {len(rows)} rows; {len(pending)} rows still require circuit recovery/freeze")
