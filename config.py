"""
config.py – central settings + self-tuning support
• Reads Zerodha keys from environment variables
• Loads the full NSE-100 universe
• Pulls live thresholds from sniper_params.json (if that file exists)
"""

import os, json, pathlib
from dotenv import load_dotenv

# ── Load local .env when running on your laptop ───────────────────────────
load_dotenv("config.env", override=False)

# ── Zerodha credentials (set in Render Environment) ───────────────────────
API_KEY       = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET") or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# ── NSE-100 universe (Nifty 50 + Nifty Next 50) ───────────────────────────
NSE100 = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","KOTAKBANK","LT","SBIN",
    "AXISBANK","BHARTIARTL","BAJFINANCE","ASIANPAINT","MARUTI","SUNPHARMA",
    "NTPC","POWERGRID","M&M","ONGC","TITAN","HCLTECH","ULTRACEMCO","TECHM",
    "DIVISLAB","JSWSTEEL","WIPRO","HINDUNILVR","BAJAJ-AUTO","CIPLA","NESTLEIND",
    "GRASIM","BRITANNIA","COALINDIA","UPL","BAJAJFINSV","ADANIPORTS","TATASTEEL",
    "HEROMOTOCO","BPCL","EICHERMOT","HDFCLIFE","DRREDDY","HINDALCO","SHREECEM",
    "SBILIFE","APOLLOHOSP","BAJAJHLDNG","DABUR","DMART","ICICIPRULI","INDUSINDBK",
    "IOC","GODREJCP","LTI","NAUKRI","PIDILITIND","PGHH","SIEMENS","SRF","VEDL",
    "ADANIENT","AMBUJACEM","AUBANK","BAJAJCON","BANDHANBNK","BERGEPAINT",
    "BIOCON","BOSCHLTD","CANBK","CHOLAFIN","COLPAL","COROMANDEL","CROMPTON",
    "DELTACORP","GAIL","GLENMARK","HINDPETRO","ICICIGI","IDEA","IGL","IRCTC",
    "LUPIN","MUTHOOTFIN","PETRONET","PNB","RBLBANK","SAIL","TRENT","TVSMOTOR",
    "UBL","UJJIVANSFB","VOLTAS","ZEEL"
]

FNO_SYMBOLS = sorted(set(NSE100))          # engine loops over this list

# ── Default Sniper-Prompt thresholds ──────────────────────────────────────
RSI_MIN        = 55
ADX_MIN        = 20
VOL_MULTIPLIER = 1.5
CMP_TOLERANCE  = 0.02
OPTION_SPOT_BAND = 0.15
DEFAULT_POP    = "85%"

# ── Self-tuning override (reads sniper_params.json if present) ────────────
PARAMS_FILE = pathlib._
