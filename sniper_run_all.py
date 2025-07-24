#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate Kite (token_manager)
  2) Inject kite into utils
  3) Run Sniper Engine → raw_trades
  4) Remap to dashboard columns → write trades.json
  5) Push to GitHub + self-tune
"""

import os
import math
import json
import base64
import requests
import pathlib

import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

# 3) Generate trades
raw_trades = generate_sniper_trades()

# 4) Remap keys for dashboard
mapping = {
    "date":    "Date",
    "symbol":  "Symbol",
    "type":    "Type",       # might come from .get("type") or .get("strategy")
    "entry":   "Entry",
    "cmp":     "CMP",
    "target":  "Target",
    "sl":      "SL",
    "pop":     "PoP",
    "status":  "Status",
    "pnl":     "P&L (₹)",
    "action":  "Action",
}

# Which columns are numeric?
numeric_cols = {"Entry","CMP","Target","SL","PoP","P&L (₹)"}

dashboard_trades = []
for t in raw_trades:
    row = {}
    for src_key, dst_key in mapping.items():
        if src_key == "type":
            # prefer explicit type field, else fallback to strategy
            v = t.get("type") if t.get("type") is not None else t.get("strategy")
        else:
            v = t.get(src_key)

        # Numeric columns → null if missing/NaN
        if dst_key in numeric_cols:
            if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
                row[dst_key] = None
            else:
                row[dst_key] = v
        else:
            # Text/date columns → empty string if missing
            row[dst_key] = v if v is not None else ""
    dashboard_trades.append(row)

# 5) Write trades.json
with open("trades.json", "w") as f:
    json.dump(dashboard_trades, f, indent=2)
print(f"💾 trades.json written with {len(dashboard_trades)} rows.")

# 6) Push to GitHub
def push_to_github(path="trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ GITHUB_TOKEN not set – skipping GitHub push.")
        return
    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
    }
    content_b64 = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    # get existing SHA
    r = requests.get(api, headers=hdrs)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {
        "message": f"Auto-update {path}",
        "content": content_b64,
        "branch":  "main",
    }
    if sha:
        payload["sha"] = sha
    res = requests.put(api, headers=hdrs, data=json.dumps(payload))
    print("✅ Pushed to GitHub." if res.status_code in (200,201)
          else f"🛑 GitHub push failed: {res.status_code}")

push_to_github()

# 7) Simple self-tuner (unchanged)
PERF = pathlib.Path("performance.json")
try:
    records = json.loads(PERF.read_text()) if PERF.exists() else []
except json.JSONDecodeError:
    records = []

if records:
    adx_trades  = [r for r in records if r.get("adx", 0) < 25]
    adx_sl_hits = [r for r in adx_trades if r.get("result") == "SL"]
    if adx_trades and len(adx_sl_hits) / len(adx_trades) > 0.60:
        new_params = {"RSI_MIN": 55, "ADX_MIN": 22, "VOL_MULTIPLIER": 1.5}
        PARAMS_FILE.write_text(json.dumps(new_params, indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️ No parameter change today.")
else:
    print("ℹ️ No performance data yet.")

print("✅ Sniper run complete.")
