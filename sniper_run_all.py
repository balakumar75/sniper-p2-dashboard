#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate Kite (token_manager)
  2) Inject kite into utils
  3) Run Sniper Engine → get raw trades
  4) Remap to dashboard columns → write trades.json
  5) Push to GitHub + self-tune
"""

import kite_patch
from token_manager import refresh_if_needed
import utils

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

import json, base64, requests, pathlib

# 3) Generate trades
raw_trades = generate_sniper_trades()

# 4) Remap keys to exactly what the dashboard needs
mapping = {
    "date":    "Date",
    "symbol":  "Symbol",
    "type":    "Type",
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
    for src_key, dst_key in mapping.items():
        # Default to “—” if missing or None
        v = t.get(src_key)
        if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
            v = "—"
        row[dst_key] = v
    dashboard_trades.append(row)

# 5) Write JSON
with open("trades.json", "w") as f:
    json.dump(dashboard_trades, f, indent=2)

print(f"💾 trades.json written with {len(dashboard_trades)} rows.")

# 6) Push back to GitHub (optional)
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
    # get existing sha if any
    r = requests.get(api, headers=hdrs)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {"message":"Auto-update trades.json","content":content,"branch":"main"}
    if sha: payload["sha"] = sha
    requests.put(api, headers=hdrs, data=json.dumps(payload))

push_to_github()

# 7) Self-tune (unchanged) …
PERF = pathlib.Path("performance.json")
records = json.loads(PERF.read_text()) if PERF.exists() else []
if records:
    adx_trades  = [r for r in records if r.get("adx",0) < 25]
    adx_sl_hits = [r for r in adx_trades if r.get("result") == "SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades) > 0.60:
        PARAMS_FILE.write_text(json.dumps({"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5},indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️  No parameter change today.")
else:
    print("ℹ️  No performance data yet.")

print("✅ Sniper run complete.")
