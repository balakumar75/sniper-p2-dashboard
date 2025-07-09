import json
from utils import fetch_cmp_batch, generate_trade_signal

NSE_100 = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "LT", "KOTAKBANK",
    "SBIN", "AXISBANK", "ITC", "BHARTIARTL", "BAJFINANCE", "ASIANPAINT",
    "HINDUNILVR", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "HCLTECH",
    "WIPRO", "POWERGRID", "NTPC", "INDUSINDBK", "JSWSTEEL", "M&M",
    "NESTLEIND", "SBILIFE", "TECHM", "UPL", "DIVISLAB", "HINDALCO",
    "TATACONSUM", "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA", "DLF",
    "GAIL", "AMBUJACEM", "ICICIPRULI", "PIDILITIND", "ADANIENT", "CIPLA",
    "EICHERMOT", "GRASIM", "BPCL", "HEROMOTOCO", "BAJAJFINSV", "HDFCLIFE"
]

def generate_sniper_trades():
    trades = []
    print("🚀 Fetching CMPs for all stocks in batch...")
    cmp_map = fetch_cmp_batch(NSE_100)

    for symbol in NSE_100:
        print(f"🔍 Processing {symbol}...")
        cmp = cmp_map.get(symbol)
        if cmp is None:
            print(f"⚠️ No CMP found for {symbol}, skipping.")
            continue
        signal = generate_trade_signal(symbol, cmp)
        if signal:
            trades.append(signal)
        else:
            print(f"⚠️ No trade signal for {symbol}")
    return trades

def save_trades_to_json(trades, filename='trades.json'):
    with open(filename, 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"✅ {len(trades)} trades saved to {filename}")
