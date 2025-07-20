"""
Central config – keep ALL tweakables here.
"""

import os

# ── Zerodha Kite credentials ──────────────────────────────────────────────
#     ▸ Never hard-code real keys!  Load from Render / GitHub Secrets.
API_KEY    = os.getenv("KITE_API_KEY",    "")
API_SECRET = os.getenv("KITE_API_SECRET", "")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")  # refreshed daily by cron

# ── Trading universe ──────────────────────────────────────────────────────
# NSE F&O stocks (NSE 50 + NSE 100) – static snapshot.
#   ▸ Replace with a DB/query if you want live universe updates.
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "LTIM", "SBIN", "AXISBANK", "MARUTI", "BEL",
    # … add the rest …
]

# ── Technical filter thresholds (Sniper Prompt v3.1) ──────────────────────
RSI_MIN          = 55
ADX_MIN          = 20
VOL_MULTIPLIER   = 1.5   # volume > 1.5× 20-day average
CMP_TOLERANCE    = 0.02  # ±2 %
OPTION_SPOT_BAND = 0.15  # ±15 %
DEFAULT_POP      = "85%"
