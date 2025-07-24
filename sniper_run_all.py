#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate with Kite
  2) Inject kite into utils
  3) Run Sniper Engine → raw_trades
  4) Remap every field, filling missing with "—" → write trades.json
  5) Push to GitHub + self-tune
"""

import os, math, json, base64, requests, pathlib
import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

# 3) Generate raw trades
raw_trades = generate_sniper_trades()

# 4) Remap to dashboard columns (always fill missing with "—")
# These are the exact column headers your dashboard expects:
COLUMNS = [
    "Date","Symbol","Type","Entry","CMP","Target",
    "SL","PoP","Status","P&L (₹)","Action"
]

dashboard_trades = []
for t in raw_trades:
    row = {}
    # ensure Type is pulled from either "type" or "strategy"
    type_val = t.get("type") if t.get("type") is not None else t.get("strategy")
    # build each column
    for col in COLUMNS:
        if col == "Date":
            v = t.get("date")
        elif col == "Symbol":
            v = t.get("symbol")
        elif col == "Type":
            v = type_val
        elif col == "Entry":
            v = t.get("entry")
        elif col == "CMP":
            v = t.get("cmp")
        elif col == "Target":
            v = t.get("target")
        elif col == "SL":
            v = t.get("sl")
        elif col == "PoP":
            v = t.get("pop")
        elif col == "Status":
            v = t.get("status")
        elif col == "P&L (₹)":
            v = t.get("pnl")
        elif col == "Action":
            v = t.get("action")
        # final fallback: if missing, None, empty, or NaN → "—"
        if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
            v = "—"
        row[col] = v
    dashboard_trades.append(row)

# 5) Write JSON
with open("trades.json","w") as f:
    json.dump(dashboard_trades, f, indent=2)
print(f"💾 trades.json written with {len(dashboard_trades)} rows.")

# 6) Push back to GitHub
def push_to_github(path="trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ GITHUB_TOKEN not set – skipping GitHub push.")
        return
    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {"Authorization":f"token {token}","Accept":"application/vnd.github.v3+json"}
    content = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    r = requests.get(api, headers=hdrs)
    sha = r.json().get("sha") if r.status_code==200 else None
    payload={"message":f"Auto-update {path}","content":content,"branch":"main"}
    if sha: payload["sha"]=sha
    res = requests.put(api, headers=hdrs, data=json.dumps(payload))
    print("✅ Pushed to GitHub." if res.status_code in (200,201) else f"🛑 GitHub push failed: {res.status_code}")

push_to_github()

# 7) Self-tuner (unchanged)
PERF = pathlib.Path("performance.json")
try:
    records = json.loads(PERF.read_text()) if PERF.exists() else []
except json.JSONDecodeError:
    records = []

if records:
    adx_trades  = [r for r in records if r.get("adx",0) < 25]
    adx_sl_hits = [r for r in adx_trades if r.get("result") == "SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades) > 0.60:
        new = {"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}
        PARAMS_FILE.write_text(json.dumps(new, indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️ No parameter change today.")
else:
    print("ℹ️ No performance data yet.")

print("✅ Sniper run complete.")
