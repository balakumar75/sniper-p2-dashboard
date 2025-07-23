#!/usr/bin/env python
"""
sniper_run_all.py
  1) Kite auth via token_manager (auto-refresh, global rate-limited)
  2) Run Sniper Engine
  3) Push trades.json to GitHub
  4) Self-tune parameters
"""

# ── imports that must come first ───────────────────────────────────────────
import kite_patch                              # global monkey-patch → rate-limits every Kite call
from token_manager import refresh_if_needed    # auto-handles tokens / renewals
from kiteconnect import exceptions as kc_ex

# ── standard libs ──────────────────────────────────────────────────────────
import os, sys, json, base64, requests, pathlib, datetime

# ── project modules ────────────────────────────────────────────────────────
from sniper_engine import generate_sniper_trades, save_trades_to_json
from config import PARAMS_FILE                 # points to sniper_params.json

# ── 1. Kite auth ───────────────────────────────────────────────────────────
try:
    kite = refresh_if_needed()                 # returns ready-to-use KiteConnect
    print(f"✅ Kite auth OK – {kite.profile()['user_name']}")
except kc_ex.TokenException as e:
    print("🛑 Kite auth failed:", e)
    sys.exit(1)

# ── 2. Generate Sniper trades ──────────────────────────────────────────────
trades = generate_sniper_trades()
save_trades_to_json(trades)
print(f"💾 trades.json written with {len(trades)} trades.")

# ── 3. Push trades.json to GitHub (optional) ───────────────────────────────
def push_to_github(path: str = "trades.json"):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️  GITHUB_TOKEN not set – skipping GitHub push.")
        return

    repo = "balakumar75/sniper-p2-dashboard"
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # read + base64-encode file
    with open(path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    # check if file already exists (need SHA for update)
    sha = None
    r = requests.get(api, headers=headers)
    if r.status_code == 200:
        sha = r.json().get("sha")

    payload = {
        "message": "Auto-update trades.json",
        "content": content_b64,
        "branch":  "main",
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(api, headers=headers, data=json.dumps(payload))
    if r.status_code in (200, 201):
        print("✅ Pushed trades.json to GitHub.")
    else:
        print(f"🛑 GitHub push failed – status {r.status_code}")

push_to_github()

# ── 4. Inline self-tuner (simple adaptive params) ──────────────────────────
PERF_FILE = pathlib.Path("performance.json")

try:
    records = json.loads(PERF_FILE.read_text()) if PERF_FILE.exists() else []
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
