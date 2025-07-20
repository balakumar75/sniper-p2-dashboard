#!/usr/bin/env python
"""
sniper_run_all.py
  1) Kite auth
  2) Run Sniper Engine
  3) Push trades.json to GitHub
  4) Self-tune parameters (no extra Render job)
"""

import os, sys, json, base64, requests, pathlib, datetime
from kiteconnect import KiteConnect, exceptions as kc_ex
from sniper_engine import generate_sniper_trades, save_trades_to_json
from config import PARAMS_FILE    # path to sniper_params.json

# ── 1. Kite auth ───────────────────────────────────────────────────────────
API_KEY = os.getenv("KITE_API_KEY") or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)
try:
    print(f"✅ Kite auth OK – {kite.profile()['user_name']}")
except kc_ex.TokenException as e:
    print("🛑 Kite auth failed:", e)
    sys.exit(1)

# ── 2. Generate trades ─────────────────────────────────────────────────────
trades = generate_sniper_trades()
save_trades_to_json(trades)
print(f"💾 trades.json written with {len(trades)} trades.")

# ── 3. Push trades.json to GitHub ──────────────────────────────────────────
def push_to_github(path="trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token: return print("⚠️  GITHUB_TOKEN not set – skipping push.")
    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    hdrs = {"Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"}
    with open(path,"rb") as f: b64 = base64.b64encode(f.read()).decode()
    sha = None
    r = requests.get(api, headers=hdrs)
    if r.status_code == 200: sha = r.json()["sha"]
    payload = {"message": "Auto-update trades.json",
               "content": b64, "branch":"main", **({"sha":sha} if sha else {})}
    ok = requests.put(api, headers=hdrs, data=json.dumps(payload))
    print("✅ Pushed trades.json to GitHub." if ok.status_code in (200,201)
          else f"🛑 GitHub push failed {ok.status_code}")

push_to_github()

# ── 4. Inline self-tuner (was sniper_learn.py) ─────────────────────────────
PERF = pathlib.Path("performance.json")
records = json.loads(PERF.read_text()) if PERF.exists() else []
if records:
    adx_trades  = [r for r in records if r.get("adx",0) < 25]
    adx_sl_hits = [r for r in adx_trades if r["result"] == "SL"]
    if adx_trades and len(adx_sl_hits)/len(adx_trades) > 0.60:
        new_params = {"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}
        PARAMS_FILE.write_text(json.dumps(new_params,indent=2))
        print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
    else:
        print("ℹ️  No parameter change today.")
else:
    print("ℹ️  No performance data yet.")

print("✅ Sniper run complete.")
