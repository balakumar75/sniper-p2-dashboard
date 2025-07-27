#!/usr/bin/env python3
"""
sniper_run_all.py

1) Authenticate with Kite (token_manager)
2) Inject kite into utils
3) Run Sniper Engine → raw trades (Title‑Case keys)
4) Normalize keys to lower‑case and write trades.json
5) Archive to trade_history.json
6) Push trades.json to GitHub
7) Simple self‑tuner
"""

import os
import json
import base64
import requests
import pathlib
from datetime import date

import kite_patch                   # apply our host URL patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE      # path to sniper_params.json

# 1) Authenticate & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

# 3) Generate raw trades
trades = generate_sniper_trades()

# 4) Normalize keys and write trades.json
normalized = []
for t in trades:
    normalized.append({
        "date":    t.get("Date"),
        "symbol":  t.get("Symbol"),
        "type":    t.get("Type"),
        "entry":   t.get("Entry"),
        "cmp":     t.get("CMP"),
        "target":  t.get("Target"),
        "sl":      t.get("SL"),
        "pop":     t.get("PoP"),
        "status":  t.get("Status"),
        "pnl":     t.get("P&L (₹)"),
        "action":  t.get("Action"),
    })

with open("trades.json", "w") as f:
    json.dump(normalized, f, indent=2)
print(f"💾 trades.json written with {len(normalized)} trades.")

# 5) Archive to trade_history.json
HIST = pathlib.Path("trade_history.json")
history = json.loads(HIST.read_text()) if HIST.exists() else []
history.append({
    "run_date": date.today().isoformat(),
    "trades":   normalized
})
HIST.write_text(json.dumps(history, indent=2))
print(f"🗄️  Appended {len(normalized)} trades to trade_history.json (now {len(history)} runs).")

# 6) Push trades.json to GitHub
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

    res = requests.put(api, headers=hdrs, data=json.dumps(payload))
    if res.status_code in (200, 201):
        print("✅ Pushed trades.json to GitHub.")
    else:
        print(f"🛑 GitHub push failed: {res.status_code}")

push_to_github()

# 7) Simple self‑tuner
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
        print("ℹ️  No parameter change today.")
else:
    print("ℹ️  No performance data yet.")

print("✅ Sniper run complete.")
