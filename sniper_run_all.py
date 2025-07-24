#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate Kite
  2) Inject kite into utils
  3) Run Sniper Engine → get raw trades (lower-case keys)
  4) Remap to upper-case headers → write trades.json
  5) Push to GitHub + self-tune
"""

import os, math, json, base64, requests, pathlib
import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# 1) Authenticate & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Load your engine
from sniper_engine import generate_sniper_trades

# 3) Generate raw trades
raw = generate_sniper_trades()

# 4) Remap to the exact column names
dashboard = []
for t in raw:
    dashboard.append({
        "Date":       t.get("date", ""),
        "Symbol":     t.get("symbol", ""),
        "Type":       t.get("type") or t.get("strategy") or "",
        "Entry":      t.get("entry", 0),
        "CMP":        t.get("cmp",   0),
        "Target":     t.get("target",0),
        "SL":         t.get("sl",    0),
        "PoP":        t.get("pop",   0),
        "Status":     t.get("status",""),
        "P&L (₹)":    t.get("pnl",   0),
        "Action":     t.get("action",""),
    })

# 5) Write trades.json
with open("trades.json", "w") as f:
    json.dump(dashboard, f, indent=2)
print(f"💾 trades.json written with {len(dashboard)} rows.")

# 6) Push to GitHub
def push_to_github(path="trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ GITHUB_TOKEN not set – skipping push.")
        return
    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {"Authorization":f"token {token}", "Accept":"application/vnd.github.v3+json"}
    content = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    resp = requests.get(api, headers=hdrs)
    sha = resp.json().get("sha") if resp.status_code==200 else None
    payload = {"message":f"Auto-update {path}", "content":content, "branch":"main"}
    if sha: payload["sha"]=sha
    r = requests.put(api, headers=hdrs, data=json.dumps(payload))
    print("✅ Pushed trades.json." if r.status_code in (200,201) else f"🛑 Push failed: {r.status_code}")

push_to_github()

# 7) Self-tune (unchanged)
PERF = pathlib.Path("performance.json")
try:
    recs = json.loads(PERF.read_text()) if PERF.exists() else []
except json.JSONDecodeError:
    recs = []

if recs:
    adx_trades  = [r for r in recs if r.get("adx",0) < 25]
    adx_sl_hits = [r for r in adx_trades if r.get("result")=="SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades) > 0.6:
        newp = {"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}
        PARAMS_FILE.write_text(json.dumps(newp, indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️ No parameter change today.")
else:
    print("ℹ️ No performance data yet.")

print("✅ Sniper run complete.")
