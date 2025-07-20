"""
utils.py  – Zerodha helpers (auth + CMP fetch)
"""

import os, sys
from datetime import datetime
from dotenv import load_dotenv
from kiteconnect import KiteConnect, exceptions as kc_ex

# ──────────────────────────────────────────────────────────────────────────
# 1. Load any local .env (ignored on Render, useful on your laptop)
# ──────────────────────────────────────────────────────────────────────────
load_dotenv("config.env", override=False)

# Accept either new or old env-var names
API_KEY      = (
    os.getenv("KITE_API_KEY") 
    or os.getenv("ZERODHA_API_KEY") 
    or ""
)
ACCESS_TOKEN = (
    os.getenv("KITE_ACCESS_TOKEN") 
    or os.getenv("ZERODHA_ACCESS_TOKEN") 
    or ""
)

# Show what the container actually sees (first 8 chars only)
print(f"🔑 utils.py using KEY: {API_KEY[:8]}…  TOKEN: {ACCESS_TOKEN[:8]}…", flush=True)

# ──────────────────────────────────────────────────────────────────────────
# 2. Initialise Kite & one-shot auth check
# ──────────────────────────────────────────────────────────────────────────
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

try:
    user_name = kite.profile()["user_name"]
    print(f"✅ Kite auth OK – user: {user_name}", flush=True)
except kc_ex.TokenException as e:
    print(f"🛑 Kite auth failed: {e}", flush=True)
    # Hard-exit so the engine doesn’t spam errors
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────
# 3. CMP helper
# ──────────────────────────────────────────────────────────────────────────
def fetch_cmp(symbol: str) -> float | None:
    """
    Return live CMP for cash or current-month futures.
      • Cash  → "NSE:RELIANCE"
      • Fut   → "NFO:RELIANCEJULFUT" (auto-month)
    """
    try:
        if symbol.upper().endswith("FUT"):
            base = symbol.split()[0]         # e.g. "RELIANCE"
            month = datetime.today().strftime("%b").upper()[:3]  # JUL, AUG…
            tradingsymbol = f"{base}{month}FUT"
            exchange = "NFO"
        else:
            tradingsymbol = symbol.upper()
            exchange = "NSE"

        quote = kite.ltp(f"{exchange}:{tradingsymbol}")
        return quote[f"{exchange}:{tradingsymbol}"]["last_price"]

    except Exception as e:
        print(f"❌ fetch_cmp error for {symbol}: {e}", flush=True)
        return None
