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
                    t["status"] = "Target"
                    t["exit_date"] = date.today().isoformat()
                    break
                if row["low"] <= sl:
                    t["status"] = "SL"
                    t["exit_date"] = date.today().isoformat()
                    break

        # Options-Strangle trades (check both legs)
        elif t["type"] == "Options-Strangle":
            # Put leg
            ptkn = utils.option_token(t["symbol"], t["put_strike"], t["date"], "PE")
            dfp  = utils.fetch_ohlc_by_token(ptkn, t["date"])
            for _, r in dfp.iterrows():
                # define your target/sl logic per leg if needed
                # e.g. if r["high"] >= some target or r["low"] <= some SL
                pass
            # Call leg - similar if desired

# Write updated history back
with open(HIST, "w") as f:
    json.dump(hist, f, indent=2)

print("✅ trade_history.json updated")
