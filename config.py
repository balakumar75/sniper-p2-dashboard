"""
config.py – central settings + self-tuning parameters
"""
import os, json, pathlib
from dotenv import load_dotenv

load_dotenv("config.env", override=False)

API_KEY       = os.getenv("KITE_API_KEY")       or os.getenv("ZERODHA_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET")    or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN")  or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# ── NSE-100 universe (full list) ──────────────────────────────────────────
NSE100 = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","KOTAKBANK","LT","SBIN",
    # … rest of your 100 symbols …
]
FNO_SYMBOLS = sorted(NSE100)

# ── Default thresholds (overridden by tuner) ──────────────────────────────
RSI_MIN, ADX_MIN, VOL_MULTIPLIER = 0, 0, 1.0

# ── Engine parameters ──────────────────────────────────────────────────────
# Allow every strangle
POPCUT = 0.0
# Generate up to 10 cash‐momentum picks
TOP_N_MOMENTUM = 10

# ── Self-tuning params file ────────────────────────────────────────────────
PARAMS_FILE = pathlib.Path(__file__).parent / "sniper_params.json"
if PARAMS_FILE.exists():
    p = json.loads(PARAMS_FILE.read_text())
    RSI_MIN        = p.get("RSI_MIN",        RSI_MIN)
    ADX_MIN        = p.get("ADX_MIN",        ADX_MIN)
    VOL_MULTIPLIER = p.get("VOL_MULTIPLIER", VOL_MULTIPLIER)
    POPCUT         = p.get("POPCUT",         POPCUT)
    TOP_N_MOMENTUM = p.get("TOP_N_MOMENTUM", TOP_N_MOMENTUM)
