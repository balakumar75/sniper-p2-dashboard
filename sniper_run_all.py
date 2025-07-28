#!/usr/bin/env python
"""
sniper_run_all.py

1) Authenticate with Kite (token_manager)
2) Inject kite into utils
3) Run Sniper Engine → trades list
4) Write trades.json + docs/trades.json
5) Archive to trade_history.json
6) Push & commit both files
7) Simple self-tuner
"""

import os, json, base64, requests, pathlib
from datetime import date

import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# JSON dump helper (casts numpy types to native ints automatically)
JSON_KW = dict(indent=2, default=int)

# 1) Auth & inject into utils
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Import engine
from sniper_engine import generate_sniper_trades

# 3) Generate trades
trades = generate_sniper_trades()

# 4) Write root trades.json
root_trades = pathlib.Path("trades.json")
root_trades.write_text(json.dumps(trades, **JSON_KW))
print(f"💾 trades.json written with {len(trades)} trades.")

# 4b) Write docs/trades.json for GitHub Pages
docs_dir    = pathlib.Path("docs")
docs_dir.mkdir(exist_ok=True)
docs_trades = docs_dir / "trades.json"
docs_trades.write_text(json.dumps(trades, **JSON_KW))
print(f"💾 docs/trades.json written with {len(trades)} trades.")

# 5) Archive to trade_history.json
hist_file = pathlib.Path("trade_history.json")
try:
    history = json.loads(hist_file.read_text()) if hist_file.exists() else []
except json.JSONDecodeError:
    history = []
history.append({"run_date": date.today().isoformat(), "trades": trades})
hist_file.write_text(json.dumps(history, **JSON_KW))
print(f"🗄️  Appended {len(trades)} trades to trade_history.json (runs={len(history)})")

# 6) Push to GitHub
def push_and_commit():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ No GITHUB_TOKEN – skipping push.")
        return

    # 6a) GitHub API push of root trades.json
    repo = "balakumar75/sniper-p2-dashboard"
    for path in ("trades.json",):
        api  = f"https://api.github.com/repos/{repo}/contents/{path}"
        hdrs = {"Authorization":f"token {token}", "Accept":"application/vnd.github.v3+json"}
        b64  = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
        # fetch existing sha if any
        resp = requests.get(api, headers=hdrs); sha = resp.json().get("sha") if resp.status_code==200 else None
        payload = {"message":f"Auto-update {path}","content":b64,"branch":"main", **({"sha":sha} if sha else {})}
        put = requests.put(api, headers=hdrs, data=json.dumps(payload))
        print("✅ Pushed",path) if put.status_code in (200,201) else print("🛑 Push failed",path,put.status_code)

    # 6b) Git commit+push docs/trades.json & trade_history.json via CLI
    os.system('git config user.name  "sniper-bot"')
    os.system('git config user.email "bot@users.noreply.github.com"')
    os.system('git add trade_history.json docs/trades.json')
    # no-op if nothing changed
    os.system('if ! git diff --cached --quiet; then git commit -m "Daily trades '+date.today().isoformat()+'" && git push origin main; else echo "No changes to commit"; fi')

push_and_commit()

# 7) Self‑tuner (unchanged)
PERF = pathlib.Path("performance.json")
try:
    records = json.loads(PERF.read_text()) if PERF.exists() else []
except json.JSONDecodeError:
    records = []

if records:
    adx_trades  = [r for r in records if r.get("adx",0)<25]
    adx_sl_hits = [r for r in adx_trades if r["result"]=="SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades)>0.60:
        new = {"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}
        PARAMS_FILE.write_text(json.dumps(new,indent=2))
        print("🔧 Raised ADX_MIN to 22 based on SL >60%")
    else:
        print("ℹ️ No parameter change today.")
else:
    print("ℹ️ No performance data yet.")

print("✅ Sniper run complete.")
