"""
config.py – central settings + self‑tuning parameters
"""
import os, json, pathlib
from dotenv import load_dotenv

load_dotenv("config.env", override=False)

API_KEY       = os.getenv("KITE_API_KEY")       or os.getenv("ZERODHA_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET")    or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN")  or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# ── NSE‑100 universe ─────────────────────────────────────────────────────────
NSE100 = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","KOTAKBANK","LT","SBIN",
    "AXISBANK","BHARTIARTL","BAJFINANCE","ASIANPAINT","MARUTI","SUNPHARMA","NTPC",
    "POWERGRID","M&M","ONGC","TITAN","HCLTECH","ULTRACEMCO","TECHM","DIVISLAB",
    "JSWSTEEL","WIPRO","HINDUNILVR","BAJAJ-AUTO","CIPLA","NESTLEIND","GRASIM",
    "BRITANNIA","COALINDIA","UPL","BAJAJFINSV","ADANIPORTS","TATASTEEL",
    "HEROMOTOCO","BPCL","EICHERMOT","HDFCLIFE","DRREDDY","HINDALCO","SHREECEM",
    "SBILIFE","APOLLOHOSP","BAJAJHLDNG","DABUR","DMART","ICICIPRULI",
    "INDUSINDBK","IOC","GODREJCP","LTIM","NAUKRI","PIDILITIND","PGHH","SIEMENS",
    "SRF","VEDL","ADANIENT","AMBUJACEM","AUBANK","BAJAJCON","BANDHANBNK",
    "BERGEPAINT","BIOCON","BOSCHLTD","CANBK","CHOLAFIN","COLPAL","COROMANDEL",
    "CROMPTON","DELTACORP","GAIL","GLENMARK","HINDPETRO","ICICIGI","IDEA","IGL",
    "IRCTC","LUPIN","MUTHOOTFIN","PETRONET","PNB","RBLBANK","SAIL","TRENT",
    "TVSMOTOR","UBL","UJJIVANSFB","VOLTAS","ZEEL"
]
FNO_SYMBOLS = sorted(NSE100)

# Production thresholds tuned for higher‑probability signals
RSI_MIN, ADX_MIN, VOL_MULTIPLIER = 60, 20, 1.5

# Options‑Strangle: require at least a 75% PoP (i.e. 25% max max‑loss chance)
POPCUT         = 0.75

# Cash‑Momentum: only pick the very top 3 by RSI (instead of 5)
TOP_N_MOMENTUM = 3

# ── Self‑tuning params file (used by your inline tuner) ─────────────────────
PARAMS_FILE = pathlib.Path(__file__).parent / "sniper_params.json"
if PARAMS_FILE.exists():
    p = json.loads(PARAMS_FILE.read_text())
    RSI_MIN        = p.get("RSI_MIN",        RSI_MIN)
    ADX_MIN        = p.get("ADX_MIN",        ADX_MIN)
    VOL_MULTIPLIER = p.get("VOL_MULTIPLIER", VOL_MULTIPLIER)
