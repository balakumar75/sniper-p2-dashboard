"""
config.py – central settings + self-tuning support
(unchanged apart from the corrected Path line)
"""

import os, json, pathlib
from dotenv import load_dotenv

load_dotenv("config.env", override=False)

# Zerodha creds
API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY", "")
API_SECRET   = os.getenv("KITE_API_SECRET") or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# NSE-100 universe (truncated here for brevity – keep your full list)
NSE100 = ["RELIANCE","TCS","HDFCBANK", ...]
FNO_SYMBOLS = sorted(set(NSE100))

# Default thresholds
RSI_MIN        = 55
ADX_MIN        = 20
VOL_MULTIPLIER = 1.5
DEFAULT_POP    = "85%"

# ── self-tuning file (fixed line) ─────────────────────────────
PARAMS_FILE = pathlib.Path(__file__).parent / "sniper_params.json"
if PARAMS_FILE.exists():
    p = json.loads(PARAMS_FILE.read_text())
    RSI_MIN        = p.get("RSI_MIN", RSI_MIN)
    ADX_MIN        = p.get("ADX_MIN", ADX_MIN)
    VOL_MULTIPLIER = p.get("VOL_MULTIPLIER", VOL_MULTIPLIER)
