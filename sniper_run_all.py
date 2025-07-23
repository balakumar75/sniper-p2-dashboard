#!/usr/bin/env python
"""
sniper_run_all.py
  1) Authenticate Kite (token_manager)
  2) Inject the Kite instance into utils   ← breaks circular import
  3) Run Sniper Engine (generate & save trades)
  4) Push trades.json to GitHub (optional)
  5) Self-tune parameters (simple)


Environment variables expected (set as GitHub Secrets):
  KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN
  GITHUB_TOKEN  – only needed if you want the file push
"""

# ── 0. Global patches & shared helpers ─────────────────────────────────────
import kite_patch                              # applies rate-limiter monkey-patch
from token_manager import refresh_if_needed    # daily access-token handling
import utils                                   # MUST come before sniper_engine

# ── 1. Kite auth ───────────────────────────────────────────────────────────
try:
    kite = refresh_if_needed()
    utils.set_kite(kite)                       # inject Kite into utils.py
    print(f"✅ Kite auth OK – {kite.profile()['user_name']}")
except Exception as e:
    raise SystemExit(f"🛑 Kite authentication failed: {e}")

# ── 2. Sniper Engine imports (safe now) ────────────────────────────────────
from sniper_engine import generate_sniper_trades, save_trades_to_json

# ── 3. Standard libs & constants ───────────────────────────────────────────
import os, sys, json, base64, requests, pathlib, datetime
from kiteconnect import exceptions as kc_ex
from config import PARAMS_FILE                 # path to sniper_params.json

# ── 4. Generate trades ─────────────────────────────────────────────────────
try:
    trades = generate_sniper_trades()
    save_trades_to_json(trades)
    print(f"💾 trades.json written with {len(trades)} trades.")
except Exception as e:
    raise SystemExit(f"🛑 Sniper Engine failed: {e}")

# ── 5. Optional: push trades.json back to GitHub ───────────────────────────
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

    with open(path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    # Check if file exists (need SHA for update)
    sha = None
    r = requests.get(api, headers=headers)
    if r.status_code == 200:
        sha = r.json().get("sha")

    payload = {
        "message": f"Auto-update {path}",
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

# ── 6. Simple self-tuner (example) ─────────────────────────────────────────
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
