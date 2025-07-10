import random

# ✅ Simulated CMP fetch (replace with Zerodha API in production)
def fetch_cmp(symbol):
    return round(random.uniform(200, 2000), 2)

# ✅ Simulated PoP Calculation
def calculate_pop(symbol, entry, target, sl):
    return round(random.uniform(80, 95), 2)

# ✅ Simulated Sector Logic
def get_sector(symbol):
    return "Sector Leader ✅" if symbol.startswith("T") else "Neutral"

# ✅ Simulated Tag Detection
def detect_tags(symbol, structure_data):
    tags = []
    if structure_data.get("rsi", 0) > 55:
        tags.append("RSI✅")
    if structure_data.get("macd") == "bullish":
        tags.append("MACD✅")
    if structure_data.get("adx", 0) > 20:
        tags.append("ADX✅")
    return tags
