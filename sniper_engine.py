# sniper_engine.py

import json
from utils import fetch_cmp, generate_trade_signal

# ✅ List of symbols to scan (F&O + Nifty 100 — you can expand this)
SYMBOLS = [
    "CIPLA", "ICICIBANK", "RELIANCE", "TCS", "INFY", "HDFCBANK", "AXISBANK", "ITC", "SBIN",
    "BAJFINANCE", "LT", "SUNPHARMA", "TITAN", "WIPRO", "DRREDDY", "ASIANPAINT", "TATASTEEL",
    "JSWSTEEL", "HINDUNILVR", "BEL", "DLF", "POWERGRID", "NTPC", "EICHERMOT", "KOTAKBANK",
    "TATAMOTORS", "HCLTECH", "ADANIENT", "ADANIPORTS", "UPL", "INDUSINDBK", "DIVISLAB", "TECHM",
    "GRASIM", "ULTRACEMCO", "NESTLEIND", "MARUTI", "BAJAJFINSV", "COALINDIA", "BRITANNIA"
]

trades = []

for symbol in SYMBOLS:
    print(f"🔍 Fetching CMP for: {symbol}")
    cmp = fetch_cmp(symbol)

    if cmp:
        trade = generate_trade_signal(symbol, cmp)
        if trade:
            trades.append(trade)
            print(f"✅ Trade generated: {symbol} @ {cmp}")
        else:
            print(f"⚠️ No trade signal returned for {symbol}")
    else:
        print(f"❌ CMP fetch failed for {symbol}")

# ✅ Save all valid trades
with open("trades.json", "w") as f:
    json.dump(trades, f, indent=2)

print(f"✅ {len(trades)} sniper trades saved to trades.json.")
