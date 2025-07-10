import os
from kiteconnect import KiteConnect
import random
from datetime import datetime, timedelta

# Load API credentials
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ✅ NSE Sector Mapping
SECTOR_MAP = {
    "CIPLA": "Pharma ✅",
    "SUNPHARMA": "Pharma ✅",
    "RELIANCE": "Energy ✅",
    "HDFCBANK": "Banking ✅",
    "ICICIBANK": "Banking ✅",
    "SBIN": "Banking ✅",
    "INFY": "IT ✅",
    "TCS": "IT ✅",
    "WIPRO": "IT ✅",
    "ITC": "FMCG ✅",
    "HINDUNILVR": "FMCG ✅",
    "LT": "Capital Goods ✅",
    "POWERGRID": "Energy ✅",
    "NTPC": "Energy ✅",
    "ASIANPAINT": "Paints ✅",
    "BAJFINANCE": "NBFC ✅",
    "AXISBANK": "Banking ✅",
    "KOTAKBANK": "Banking ✅",
    "TITAN": "Consumer ✅",
    "TATAMOTORS": "Auto ✅",
    "JSWSTEEL": "Metals ✅",
    "TATASTEEL": "Metals ✅",
    "DRREDDY": "Pharma ✅",
    "BEL": "Defense ✅",
    "HAL": "Defense ✅",
    "DLF": "Realty ✅",
    "COLPAL": "FMCG ✅",
    "ZEEL": "Media ✅",
    "IRCTC": "Railways ✅"
    # 🔁 Extend as needed
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
    pop_score = random.choice([85, 87, 90, 92])
    sector = SECTOR_MAP.get(symbol, "Unknown")

    # 📌 Simulated Indicator Tagging
    tags = []

    if random.random() > 0.3:
        tags.append("RSI > 55")
    if random.random() > 0.4:
        tags.append("VWAP Support")
    if random.random() > 0.5:
        tags.append("OBV Confirmed")
    if random.random() > 0.6:
        tags.append("MACD Bullish")
    
    # 🔥 Simulated Squeeze Logic
    if random.random() > 0.85:
        tags.append("Squeeze On – Waiting")
    elif random.random() > 0.9:
        tags.append("Squeeze Fired – Bullish")

    trade = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'symbol': f"{symbol} JUL FUT",
        'type': 'Futures',
        'entry': entry,
        'target': target,
        'sl': sl,
        'pop': f"{pop_score}%",
        'sector': sector,
        'tags': tags,
        'expiry': (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d"),
        'status': 'Open',
        'exit_date': '-',
        'holding_days': '-',
        'pnl': '–',
        'return_pct': '-',
        'action': 'Buy'
    }

    return trade
