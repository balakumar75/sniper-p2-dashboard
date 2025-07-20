"""
Central config – Zerodha keys are read from env vars.
Includes complete NSE-100 universe (as of Jul-20-2025).
"""

import os
from dotenv import load_dotenv

load_dotenv("config.env", override=False)

# ── Zerodha credentials ───────────────────────────────────────────
API_KEY       = os.getenv("KITE_API_KEY") or os.getenv("ZERODHA_API_KEY", "")
API_SECRET    = os.getenv("KITE_API_SECRET") or os.getenv("ZERODHA_API_SECRET", "")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN", "")

# ── NSE-100 universe  ─────────────────────────────────────────────
NSE100 = [
    # Nifty 50 + Nifty Next 50 tickers (cash symbols)
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","KOTAKBANK","LT",
    "SBIN","AXISBANK","BHARTIARTL","BAJFINANCE","ASIANPAINT","MARUTI",
    "SUNPHARMA","NTPC","POWERGRID","M&M","ONGC","TITAN","HCLTECH","ULTRACEMCO",
    "TECHM","DIVISLAB","JSWSTEEL","WIPRO","HINDUNILVR","BAJAJ-AUTO","CIPLA",
    "NESTLEIND","GRASIM","BRITANNIA","COALINDIA","UPL","BAJAJFINSV","ADANIPORTS",
    "TATASTEEL","HEROMOTOCO","BPCL","EICHERMOT","HDFCLIFE","DRREDDY","HINDALCO",
    "SHREECEM","SBILIFE","APOLLOHOSP","BAJAJHLDNG","DABUR","DMART","ICICIPRULI",
    "INDUSINDBK","IOC","GODREJCP","LTI","NAUKRI","PIDILITIND","PGHH","SIEMENS",
    "SRF","VEDL","ADANIENT","AMBUJACEM","AUBANK","BAJAJCON","BANDHANBNK",
    "BERGEPAINT","BIOCON","BOSCHLTD","CANBK","CHOLAFIN","COLPAL","COROMANDEL",
    "CROMPTON","DELTACORP","GAIL","GLENMARK","HINDPETRO","ICICIGI","IDEA",
    "IGL","IRCTC","LUPIN","MUTHOOTFIN","PETRONET","PNB","RBLBANK","SAIL",
    "TRENT","TVSMOTOR","UBL","UJJIVANSFB","VOLTAS","ZEEL"
]

# For now the engine scans *all* NSE-100 stocks
FNO_SYMBOLS = sorted(set(NSE100))

# ── Sniper thresholds ────────────────────────────────────────────
RSI_MIN          = 55
ADX_MIN          = 20
VOL_MULTIPLIER   = 1.5
CMP_TOLERANCE    = 0.02
OPTION_SPOT_BAND = 0.15
DEFAULT_POP      = "85%"
