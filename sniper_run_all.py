#!/usr/bin/env python
"""
sniper_run_all.py – wrapper that:
  1) shows the env keys in use
  2) verifies Kite auth once
  3) runs the Sniper Engine
"""

import os
import sys
from kiteconnect import KiteConnect, exceptions as kc_ex

from sniper_engine import generate_sniper_trades, save_trades_to_json

# ───────────────────────────────────────────────────────────────────
# 1. Show which credentials this container sees
# ───────────────────────────────────────────────────────────────────
API_KEY      = os.getenv("KITE_API_KEY", "")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")

print(f"🔑 KEY: {API_KEY[:8]}…   TOKEN: {ACCESS_TOKEN[:8]}…", flush=True)

if not API_KEY or not ACCESS_TOKEN:
    print("🛑  KITE_API_KEY or KITE_ACCESS_TOKEN not set in environment.", flush=True)
    sys.exit(1)

# ───────────────────────────────────────────────────────────────────
# 2. One-shot Kite authentication check
# ───────────────────────────────────────────────────────────────────
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

try:
    user = kite.profile()["user_name"]
    print(f"✅ Kite auth OK  –  user: {user}", flush=True)
except kc_ex.TokenException as e:
    print(f"🛑  Kite auth failed: {e}", flush=True)
    sys.exit(1)

# ───────────────────────────────────────────────────────────────────
# 3. Run the Sniper Engine
# ───────────────────────────────────────────────────────────────────
print("🚀 Sniper Engine Starting...", flush=True)

try:
    trades = generate_sniper_trades()
    print(f"✅ Trades generated: {len(trades)}", flush=True)

    if trades:
        print("🔍 Preview of 1st trade:", trades[0], flush=True)
    else:
        print("⚠️  No trades generated. Check sniper filters or logic.", flush=True)

    save_trades_to_json(trades)
    print("💾 trades.json saved successfully.", flush=True)
except Exception as e:
    print("❌ Error during Sniper Engine run:", e, flush=True)
    sys.exit(1)

print("✅ Sniper run complete.", flush=True)
