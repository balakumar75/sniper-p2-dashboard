#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate Kite
  2) Inject kite into utils
  3) Run Sniper Engine → raw_trades (lower-case keys)
  4) Write trades.json with those lower-case keys
  5) Push to GitHub + self-tune
"""

import os, json, base64, requests, pathlib
import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

# 3) Generate raw trades (each dict uses keys: 
#    date, symbol, type, entry, cmp, target, sl, pop, status, pnl, action)
trades = generate_sniper_trades()

# 4) Write trades.json directly
with open("trades.json", "w") as f:
    json.dump(trades, f, indent=2)
print(f"💾 trades.json written with {len(trades)} trades.")

# 5) Push to GitHub (if GITHUB_TOKEN is set)
def push_to_github(path="trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return
    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
    }
    content = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    r = requests.get(api, headers=hdrs)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {
        "message": f"Auto-update {path}",
        "content": content,
        "branch":  "main",
    }
    if sha:
        payload["sha"] = sha
    requests.put(api, headers=hdrs, data=json.dumps(payload))

push_to_github()

# 6) Self-tuner (unchanged)…
PERF = pathlib.Path("performance.json")
try:
    records = json.loads(PERF.read_text()) if PERF.exists() else []
except json.JSONDecodeError:
    records = []
if records:
    adx_trades  = [r for r in records if r.get("adx",0) < 25]
    adx_sl_hits = [r for r in adx_trades if r.get("result") == "SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades) > 0.60:
        PARAMS_FILE.write_text(json.dumps({"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}, indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️ No parameter change today.")
else:
    print("ℹ️ No performance data yet.")

print("✅ Sniper run complete.")
