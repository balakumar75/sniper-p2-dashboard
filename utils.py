import os
import random
from datetime import datetime
from kiteconnect import KiteConnect

# Load API credentials
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ✅ NSE Sector Mapping (extend as needed)
SECTOR_MAP = {
    "CIPLA": "Pharma",
    "SUNPHARMA": "Pharma",
    "RELIANCE": "Energy",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "INFY": "IT",
    "TCS": "IT",
    "WIPRO": "IT",
    "ITC": "FMCG",
    "HINDUNILVR": "FMCG",
    "LT": "Capital Goods",
    "POWERGRID": "Energy",
    "NTPC": "Energy",
    "ASIANPAINT": "Paints",
    "BAJFINANCE": "NBFC",
    "AXISBANK": "Banking",
    "KOTAKBANK": "Banking",
    "TITAN": "Consumer",
    "EICHERMOT": "Auto",
    "TATAMOTORS": "Auto",
    "TATASTEEL": "Metals",
    "JSWSTEEL": "Metals",
    "ADANIENT": "Conglomerate",
    "ADANIPORTS": "Infrastructure",
    "DRREDDY": "Pharma",
    "COLPAL": "FMCG",
    "BEL": "Defense",
    "HAL": "Defense",
    "DLF": "Realty",
    "GAIL": "Oil & Gas",
    "IRCTC": "Railways",
    "MCX": "Exchange",
    "IDFCFIRSTB": "Banking",
    "ZEEL": "Media"
}

def fetch_cmp(symbol):
    try:
        instrument = f"NSE:{symbol}"
        quote = kite.ltp(instrument)
        return quote[instrument]['last_price']
    except Exception as e:
        print(f"❌ Error fetching CMP for {symbol}: {e}")
        return None

def generate_trade_signal(symbol, cmp):
    if cmp is None:
        return None

    entry = round(cmp, 2)
    target = round(cmp * 1.018, 2)
    sl = round(cmp * 0.985, 2)
    pop_score = random.choice([83, 85, 87, 90, 92])
    sector = SECTOR_MAP.get(symbol, "Unknown")

    trade = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'symbol': f"{symbol} JUL FUT",
        'type': 'Futures",
        'entry': entry,
        'target': target,
        'sl': sl,
        'pop': f"{pop_score}%",
        'sector': f"{sector} ✅",
        'expiry': "July 2025",
        'status': "Open",
        'pnl': "–",
        'action': 'Buy'
    }

    return trade
