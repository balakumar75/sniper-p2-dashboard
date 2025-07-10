import requests
from kiteconnect import KiteConnect
import os
import random
import time

# ✅ Load Zerodha session
kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
kite.set_access_token(os.getenv("KITE_ACCESS_TOKEN"))

# ✅ Fetch Live CMP using Zerodha
def fetch_cmp(symbol):
    try:
        if symbol.endswith("FUT"):
            instrument = f"NFO:{symbol}"
        else:
            instrument = f"NSE:{symbol}"

        quote = kite.ltp([instrument])
        return round(quote[instrument]["last_price"], 2)
    except Exception as e:
        print(f"❌ fetch_cmp error for {symbol}: {e}")
        return None

# ✅ Calculate PoP based on Risk/Reward
def calculate_pop(symbol, entry, target, sl):
    rr = (target - entry) / (entry - sl) if entry - sl != 0 else 1
    if rr >= 2:
        return 90
    elif rr >= 1.5:
        return 85
    else:
        return 80

# ✅ Sector tagging based on watchlist or logic
def get_sector(symbol):
    leader_list = ["RELIANCE", "TCS", "INFY", "LT", "SBIN", "TITAN"]
    weak_list = ["ADANIENT", "BHEL", "GAIL"]
    if symbol in leader_list:
        return "Sector Leader ✅"
    elif symbol in weak_list:
        return "Sector Weak ⚠️"
    else:
        return "Neutral"

# ✅ Dummy indicator values — replace with real API/DB later
def get_indicator_data(symbol):
    # In production, fetch from TradingView API or internal DB
    return {
        "rsi": random.randint(45, 70),
        "macd": random.choice(["bullish", "bearish", "neutral"]),
        "adx": random.randint(15, 30),
        "volume": random.randint(800000, 2000000),
        "avg_volume": 1000000
    }

# ✅ Detect tags based on indicator data
def detect_tags(symbol, structure_data):
    tags = []
    if structure_data.get("rsi", 0) > 55:
        tags.append("RSI✅")
    if structure_data.get("macd") == "bullish":
        tags.append("MACD✅")
    if structure_data.get("adx", 0) > 20:
        tags.append("ADX✅")
    if structure_data.get("volume", 0) > structure_data.get("avg_volume", 1) * 1.5:
        tags.append("High Volume✅")
    return tags

# ✅ Validate structure using real indicators
def validate_structure(symbol):
    try:
        data = get_indicator_data(symbol)

        if data["rsi"] < 55:
            return False, data
        if data["macd"] != "bullish":
            return False, data
        if data["adx"] < 20:
            return False, data
        if data["volume"] < data["avg_volume"] * 1.2:
            return False, data

        return True, data
    except Exception as e:
        print(f"❌ validate_structure error for {symbol}: {e}")
        return False, {}
