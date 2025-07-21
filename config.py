"""
config.py – central settings + self-tuning parameters
"""

import os, json, pathlib
from dotenv import load_dotenv

# ── Load optional local .env (ignored on Render) ──────────────────────────
load_dotenv("config.env", override=False)

# ── Zerodha credentials (read from Render env) ───────────────────────────
API_KEY       = os.getenv("KITE_API_KEY")       or os.getenv("ZERODHA_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET")    or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN")  or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# ── NSE-100 universe (Nifty 50 + Nifty Next 50) ──────────────────────────
NSE100 = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","KOTAKBANK","LT","SBIN",
    "AXISBANK","BHARTIARTL","BAJFINANCE","ASIANPAINT","MARUTI","SUNPHARMA","NTPC",
    "POWERGRID","M&M","ONGC","TITAN","HCLTECH","ULTRACEMCO","TECHM","DIVISLAB",
    "JSWSTEEL","WIPRO","HINDUNILVR","BAJAJ-AUTO","CIPLA","NESTLEIND","GRASIM",
    "BRITANNIA","COALINDIA","UPL","BAJAJFINSV","ADANIPORTS","TATASTEEL",
    "HEROMOTOCO","BPCL","EICHERMOT","HDFCLIFE","DRREDDY","HINDALCO","SHREECEM",
    "SBILIFE","APOLLOHOSP","BAJAJHLDNG","DABUR","DMART","ICICIPRULI",
    "INDUSINDBK","IOC","GODREJCP","LTI","NAUKRI","PIDILITIND","PGHH","SIEMENS",
    "SRF","VEDL","ADANIENT","AMBUJACEM","AUBANK","BAJAJCON","BANDHANBNK",
    "BERGEPAINT","BIOCON","BOSCHLTD","CANBK","CHOLAFIN","COLPAL","COROMANDEL",
    "CROMPTON","DELTACORP","GAIL","GLENMARK","HINDPETRO","ICICIGI","IDEA","IGL",
    "IRCTC","LUPIN","MUTHOOTFIN","PETRONET","PNB","RBLBANK","SAIL","TRENT",
    "TVSMOTOR","UBL","UJJIVANSFB","VOLTAS","ZEEL"
]

# Engine scans this sorted list
FNO_SYMBOLS = sorted(NSE100)

# ── Default Sniper-Prompt thresholds (overridden by tuner) ───────────────
RSI_MIN        = 55
ADX_MIN        = 20
VOL_MULTIPLIER = 1.5
DEFAULT_POP    = "85%"

# ── Self-tuning parameters file (written by nightly tuner) ───────────────
PARAMS_FILE = pathlib.Path(__file__).parent / "sniper_params.json"
if PARAMS_FILE.exists():
    params = json.loads(PARAMS_FILE.read_text())
    RSI_MIN        = params.get("RSI_MIN",        RSI_MIN)
    ADX_MIN        = params.get("ADX_MIN",        ADX_MIN)
    VOL_MULTIPLIER = params.get("VOL_MULTIPLIER", VOL_MULTIPLIER)
