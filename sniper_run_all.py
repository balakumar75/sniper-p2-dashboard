#!/usr/bin/env python
"""
sniper_run_all.py
  1) Verify Kite auth
  2) Run Sniper Engine
  3) Push trades.json to GitHub (uses $GITHUB_TOKEN)
"""

import os, sys, json, base64, requests
from kiteconnect import KiteConnect, exceptions as kc_ex
from sniper_engine import generate_sniper_trades, save_trades_to_json

# ──────────────────────────────────────────────────────────────
# 1. Kite authentication check
# ──────────────────────────────────────────────────────────────
API_KEY = os.getenv("KITE_API_KEY") or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

try:
    user = kite.profile()["user_name"]
    print(f"✅ Kite auth OK – {user}", flush=True)
except kc_ex.TokenException as e:
    print("🛑 Kite auth failed:", e, flush=True)
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# 2. Run Sniper Engine & save file
# ──────────────────────────────────────────────────────────────
trades = generate_sniper_trades()
save_trades_to_json(trades)
print(f"💾 trades.json written with {len(trades)} trades.", flush=True)

# ──────────────────────────────────────────────────────────────
# 3. Push trades.json to GitHub main branch
# ──────────────────────────────────────────────────────────────
def push_to_github(path: str = "trades.json") -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️  GITHUB_TOKEN not set – skipping Git push.", flush=True)
        return

    repo = "balakumar75/sniper-p2-dashboard"       # ← adjust if repo name differs
    api  = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
    }

    # Prepare file content
    with open(path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    # Get current SHA (if file already exists)
    sha = None
    r = requests.get(api, headers=headers)
    if r.status_code == 200:
        sha = r.json()["sha"]

    payload = {
        "message": "Auto-update trades.json",
        "content": content_b64,
        "branch":  "main",
        **({"sha": sha} if sha else {})
    }

    resp = requests.put(api, headers=headers, data=json.dumps(payload))
    if resp.status_code in (200, 201):
        print("✅ Pushed trades.json to GitHub.", flush=True)
    else:
        print(f"🛑 GitHub push failed: {resp.status_code} – {resp.text}", flush=True)

push_to_github()
print("✅ Sniper run complete.", flush=True)
