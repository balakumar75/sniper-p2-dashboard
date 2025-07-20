"""
config.py  – central place for:
  • secrets coming from your existing config.env/.env
  • Sniper threshold constants & stock universe
"""

import os
from dotenv import load_dotenv

# Load your existing env file (Render & local both supported)
load_dotenv("config.env", override=False)   # or just ".env" if that’s the name

# ── Zerodha credentials (already in config.env) ───────────────────────────
API_KEY       = os.getenv("KITE_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN", "")    # cron-refreshed daily

# ── F&O universe (static snapshot for now) ────────────────────────────────
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "LTIM", "SBIN", "AXISBANK", "MARUTI", "BEL",
    # …add the rest or load dynamically later…
]

# ── Sniper-Prompt v3.1 thresholds ────────────────────────────────────────
RSI_MIN          = 55
ADX_MIN          = 20
VOL_MULTIPLIER   = 1.5      # volume > 1.5× 20-day average
CMP_TOLERANCE    = 0.02     # ±2 %
OPTION_SPOT_BAND = 0.15     # ±15 %
DEFAULT_POP      = "85%"
