import os
import random
from kiteconnect import KiteConnect

# Load credentials from environment variables
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def fetch_cmp_batch(symbols):
    try:
        instrument_list = [f"NSE:{symbol}" for symbol in symbols]
        ltp_data = kite.ltp(instrument_list)
        cmp_map = {s.split(":")[1]: ltp_data[s]['last_price'] for s in ltp_data}
        return cmp_map
    except Exception as e:
        print(f"❌ Error fetching batch CMPs: {e}")
        return {}

def generate_trade_signal(symbol, cmp):
    if cmp is None:
        return None

    entry = round(cmp, 2)
    target = round(cmp * 1.018, 2)
    sl = round(cmp * 0.985, 2)
    pop_score = random.choice([80, 82, 85, 87, 88, 90])
    pop = f"{pop_score}%"

    return {
        'symbol': f"{symbol} JUL FUT",
        'type': 'Futures',
        'entry': entry,
        'target': target,
        'sl': sl,
        'pop': pop,
        'action': 'Buy'
    }
