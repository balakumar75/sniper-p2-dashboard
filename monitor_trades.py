#!/usr/bin/env python3
"""
monitor_trades.py

Reads trade_history.json and marks each Open trade as Target or SL.
"""
import json
from datetime import date
import utils

HIST = "trade_history.json"
hist = json.loads(open(HIST).read())

for run in hist:
    for t in run["trades"]:
        if t.get("status") != "Open":
            continue

        # Cash-Momentum & Futures trades
        if t["type"] in ("Cash-Momentum", "Futures"):
            df = utils.fetch_ohlc(t["symbol"], 90)
            entry, tgt, sl = t["entry"], t["target"], t["sl"]
            for _, row in df.iterrows():
                if row["high"] >= tgt:
                    t["status"]    = "Target"
                    t["exit_date"] = date.today().isoformat()
                    break
                if row["low"] <= sl:
                    t["status"]    = "SL"
                    t["exit_date"] = date.today().isoformat()
                    break

        # Options-Strangle trades (if you want per-leg tracking, flesh this out)
        elif t["type"] == "Options-Strangle":
            # placeholder for leg-by-leg checks
            pass

# Write updated history back
with open(HIST, "w") as f:
    json.dump(hist, f, indent=2)

print("✅ trade_history.json updated")
