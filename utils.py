import json
import datetime
from kiteconnect import KiteConnect

# ✅ Initialize Kite client using access token from token.txt
def get_kite_client():
    with open("token.txt", "r") as f:
        access_token = f.read().strip()

    api_key = "v5h2it4guguvb2pc"  # Your actual Kite API Key
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite

# ✅ Fetch Current Market Price
def fetch_cmp(kite, symbol):
    try:
        if symbol.endswith("FUT"):
            instrument = f"NFO:{symbol}"
        else:
            instrument = f"NSE:{symbol}"

        response = kite.ltp(instrument)
        data = response.get(instrument, {})
        return data.get("last_price", None)

    except Exception as e:
        print(f"❌ Error fetching CMP for {symbol}: {str(e)}")
        return None

# ✅ Generate basic trade signal (placeholder logic — replace with sniper rules)
def generate_trade_signal(symbol, cmp):
    if cmp is None:
        return None

    trade = {
        "symbol": symbol,
        "entry": round(cmp, 2),
        "cmp": round(cmp, 2),
        "target": round(cmp * 1.03, 2),
        "sl": round(cmp * 0.97, 2),
        "pop": "85%",
        "action": "Buy",
        "type": "Futures",
        "sector": "Auto ✅",
        "tags": ["RSI > 55", "ADX > 20"],
        "expiry": "Monthly",
        "status": "Open",
        "date": str(datetime.date.today())
    }
    return trade
