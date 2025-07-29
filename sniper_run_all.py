#!/usr/bin/env python
"""
sniper_run_all.py

1) Authenticate & inject
2) Run Sniper Engine → raw trades (no dates here)
3) Preserve entry_date from docs/trades.json
4) Write root + docs/trades.json
5) Archive to trade_history.json
6) Push & commit
"""

import os, json, base64, requests, pathlib
from datetime import date

import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

# JSON dump helper (casts numpy types to native ints)
JSON_KW = dict(indent=2, default=int)

# 1) Authenticate & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Generate fresh trades (they do NOT include any date)
from sniper_engine import generate_sniper_trades
new_trades = generate_sniper_trades()

# 3) Load yesterday’s open trades to preserve entry_date
docs_dir  = pathlib.Path("docs")
docs_dir.mkdir(exist_ok=True)
docs_file = docs_dir / "trades.json"

if docs_file.exists():
    old_trades = json.loads(docs_file.read_text())
else:
    old_trades = []

# build a map: (symbol,type) → entry_date
entry_map = {
    (t["symbol"], t["type"]): t.get("entry_date")
    for t in old_trades
}

today_iso = date.today().isoformat()
# assign entry_date: preserve if present, else today
for t in new_trades:
    key = (t["symbol"], t["type"])
    t["entry_date"] = entry_map.get(key, today_iso)

# 4a) Write root trades.json
root_file = pathlib.Path("trades.json")
root_file.write_text(json.dumps(new_trades, **JSON_KW))
print(f"💾 trades.json written with {len(new_trades)} trades.")

# 4b) Write docs/trades.json
docs_file.write_text(json.dumps(new_trades, **JSON_KW))
print(f"💾 docs/trades.json written with {len(new_trades)} trades.")

# 5) Archive to trade_history.json
hist_file = pathlib.Path("trade_history.json")
try:
    history = json.loads(hist_file.read_text()) if hist_file.exists() else []
except json.JSONDecodeError:
    history = []

# append full snapshot with entry_date
history.append({
    "run_date":     today_iso,
    "open_trades":  new_trades
})
hist_file.write_text(json.dumps(history, **JSON_KW))
print(f"🗄️  Appended {len(new_trades)} trades to trade_history.json (runs={len(history)})")

# 6) Push to GitHub: API push for root, CLI for docs & history
def push_and_commit():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ GITHUB_TOKEN not set – skipping push.")
        return

    repo = "balakumar75/sniper-p2-dashboard"

    # 6a) GitHub API for root trades.json
    api_base = f"https://api.github.com/repos/{repo}/contents"
    for fn in ("trades.json",):
        path = api_base + f"/{fn}"
        hdrs = {"Authorization":f"token {token}",
                "Accept":"application/vnd.github.v3+json"}
        b64   = base64.b64encode(pathlib.Path(fn).read_bytes()).decode()
        resp  = requests.get(path, headers=hdrs)
        sha   = resp.json().get("sha") if resp.status_code==200 else None
        payload = {
            "message": f"Auto-update {fn}",
            "content": b64,
            "branch":  "main",
            **({"sha": sha} if sha else {})
        }
        put = requests.put(path, headers=hdrs, data=json.dumps(payload))
        print("✅ Pushed", fn) if put.status_code in (200,201) else print("🛑 Push failed", fn)

    # 6b) CLI commit for docs/trades.json & trade_history.json
    os.system('git config user.name  "sniper-bot"')
    os.system('git config user.email "bot@users.noreply.github.com"')
    os.system('git add docs/trades.json trade_history.json')
    os.system(
        'if ! git diff --cached --quiet; then '
        'git commit -m "Daily trades '+today_iso+'" && '
        'git pull --rebase origin main && '
        'git push origin main; '
        'else echo "No changes to commit"; fi'
    )

push_and_commit()

print("✅ Sniper run complete.")
