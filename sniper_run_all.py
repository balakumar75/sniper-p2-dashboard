#!/usr/bin/env python
"""
sniper_run_all.py

1) Authenticate & inject
2) Run engine → trades
3) Write root + docs/trades.json
4) Archive to trade_history.json
5) Push & commit
"""

import os, json, base64, requests, pathlib
from datetime import date

import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# helper to JSON‑dump numpy types
JSON_KW = dict(indent=2, default=int)

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Run engine
from sniper_engine import generate_sniper_trades
trades = generate_sniper_trades()

# 3a) Write root trades.json
path_root = pathlib.Path("trades.json")
path_root.write_text(json.dumps(trades, **JSON_KW))
print(f"💾 trades.json with {len(trades)} trades.")

# 3b) Write docs/trades.json
docs = pathlib.Path("docs")
docs.mkdir(exist_ok=True)
path_docs = docs / "trades.json"
path_docs.write_text(json.dumps(trades, **JSON_KW))
print(f"💾 docs/trades.json with {len(trades)} trades.")

# 4) Archive
hist = pathlib.Path("trade_history.json")
try:
    history = json.loads(hist.read_text()) if hist.exists() else []
except:
    history = []
history.append({"entry_date": date.today().isoformat(), "trades": trades})
hist.write_text(json.dumps(history, **JSON_KW))
print(f"🗄️  Appended to trade_history.json (runs={len(history)})")

# 5) Push & commit via GitHub API + CLI
def push_and_commit():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ No GITHUB_TOKEN – skipping push.")
        return

    repo = "balakumar75/sniper-p2-dashboard"
    for fn in ("trades.json",):
        api = f"https://api.github.com/repos/{repo}/contents/{fn}"
        hdr = {"Authorization":f"token {token}", "Accept":"application/vnd.github.v3+json"}
        b64 = base64.b64encode(pathlib.Path(fn).read_bytes()).decode()
        r = requests.get(api, headers=hdr)
        sha = r.json().get("sha") if r.status_code==200 else None
        payload = {"message":f"Auto-update {fn}","content":b64,"branch":"main", **({"sha":sha} if sha else {})}
        res = requests.put(api, headers=hdr, data=json.dumps(payload))
        print("✅ Pushed", fn) if res.status_code in (200,201) else print("❌ Push failed", fn)

    os.system('git config user.name  "sniper-bot"')
    os.system('git config user.email "bot@users.noreply.github.com"')
    os.system('git add trade_history.json docs/trades.json')
    os.system('if ! git diff --cached --quiet; then git commit -m "Daily trades '+date.today().isoformat()+'" && git push origin main; fi')

push_and_commit()

print("✅ Sniper run complete.")
