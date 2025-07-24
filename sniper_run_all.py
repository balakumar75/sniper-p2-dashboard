#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate with Kite
  2) Inject kite into utils
  3) Run Sniper Engine → raw_trades
  4) Remap keys (handling both "type" and "strategy") → trades.json
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

# 1) Kite auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import your engine
from sniper_engine import generate_sniper_trades

# 3) Generate raw trades
raw_trades = generate_sniper_trades()

# 4) Remap for dashboard
# Dashboard expects these exact columns:
mapping = {
    "date":    "Date",
    "symbol":  "Symbol",
    "type":    "Type",       # we’ll pull from t["type"] or t["strategy"]
    "entry":   "Entry",
    "cmp":     "CMP",
    "target":  "Target",
    "sl":      "SL",
    "pop":     "PoP",
    "status":  "Status",
    "pnl":     "P&L (₹)",
    "action":  "Action",
}

dashboard_trades = []
for t in raw_trades:
    row = {}
    for src, dst in mapping.items():
        if src == "type":
            # prefer t["type"], fallback to t["strategy"]
            v = t.get("type") if t.get("type") is not None else t.get("strategy")
        else:
            v = t.get(src)

        # replace None/empty/NaN with dash
        if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
            v = "—"
        row[dst] = v
    dashboard_trades.append(row)

# 5) Write the JSON file
with open("trades.json", "w") as f:
    json.dump(dashboard_trades, f, indent=2)
print(f"💾 trades.json written with {len(dashboard_trades)} rows.")

# 6) Push to GitHub (optional)
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
    # fetch existing SHA if any
    r = requests.get(api, headers=hdrs)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": f"Auto-update {path}",
        "content": content_b64,
        "branch":  "main",
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(api, headers=hdrs, data=json.dumps(payload))
    if resp.status_code in (200, 201):
        print("✅ Pushed to GitHub.")
    else:
        print(f"🛑 GitHub push failed: {resp.status_code}")

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
