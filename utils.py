import os
import datetime
import random
from kiteconnect import KiteConnect

# Load API credentials from environment variables
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

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
    pop_score = random.choice([82, 85, 87, 88, 90])
    today = datetime.date.today().strftime("%Y-%m-%d")

    trade = {
        'date': today,
        'symbol': f"{symbol} JUL FUT",
        'type': 'Futures',
        'entry': entry,
        'target': target,
        'sl': sl,
        'pop': f"{pop_score}%",
        'action': 'Buy',
        'sector': '🔍 Unknown',         # Placeholder, to be filled by Sector Rotation Engine
        'tags': ['💡 Basic Structure'], # Placeholder, will be enhanced later
        'expiry': 'July Monthly',
        'status': 'Open',
        'pnl': None
    }

    return trade
