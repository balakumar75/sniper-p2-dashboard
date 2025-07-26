#!/usr/bin/env python3
"""
monitor_trades.py

Marks Open trades in trade_history.json as Target or SL if hit.
"""
import json
from datetime import date
import utils

H="trade_history.json"
hist=json.loads(open(H).read())
for run in hist:
    for t in run["trades"]:
        if t.get("status")!="Open": continue
        if t["type"] in ("Cash-Momentum","Futures"):
            df=utils.fetch_ohlc(t["symbol"],90)
            if df is None: continue
            for _,r in df.iterrows():
                if r["high"]>=t.get("Target",0):
                    t["status"]="Target"; t["exit_date"]=date.today().isoformat(); break
                if r["low"]<=t.get("SL",0):
                    t["status"]="SL"; t["exit_date"]=date.today().isoformat(); break
        # Options-Strangle leg‑by‑leg logic can be added here
with open(H,"w") as f: json.dump(hist,f,indent=2)
print("✅ trade_history.json updated")
