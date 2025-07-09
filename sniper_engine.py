import json
import time
from utils import fetch_cmp, generate_trade_signal

# ✅ Full NSE F&O Top 100 Stocks
NSE_100 = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "LT", "KOTAKBANK", "SBIN", "AXISBANK", "ITC",
    "BHARTIARTL", "BAJFINANCE", "ASIANPAINT", "HINDUNILVR", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO",
    "HCLTECH", "WIPRO", "POWERGRID", "NTPC", "INDUSINDBK", "JSWSTEEL", "M&M", "NESTLEIND", "SBILIFE",
    "TECHM", "UPL", "DIVISLAB", "HINDALCO", "TATACONSUM", "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA",
    "DLF", "GAIL", "AMBUJACEM", "ICICIPRULI", "HDFCLIFE", "ADANIENT", "ADANIPORTS", "COALINDIA", "HEROMOTOCO",
    "CIPLA", "BAJAJFINSV", "EICHERMOT", "GRASIM", "BPCL", "SHREECEM", "ONGC", "SBICARD", "HAVELLS", "PIDILITIND",
    "BAJAJ-AUTO", "DMART", "DRREDDY", "INDIGO", "CHOLAFIN", "TVSMOTOR", "ICICIGI", "TORNTPHARM", "BIOCON", "LTI",
    "LTTS", "NAUKRI", "ZOMATO", "SRF", "BOSCHLTD", "TRENT", "BANKBARODA", "CROMPTON", "CONCOR", "HAL", "CANBK",
    "FEDERALBNK", "BEL", "PAGEIND", "POLYCAB", "RECLTD", "MFSL", "BANDHANBNK", "PNB", "AMARAJABAT", "AUBANK",
    "BALRAMCHIN", "ESCORTS", "INDUSTOWER", "INDIAMART", "IDFCFIRSTB", "MUTHOOTFIN", "IRCTC", "MCX", "HINDPETRO",
    "GUJGASLTD", "ZEEL", "IEX", "COLPAL"
]

def generate_sniper_trades():
    trades = []
    for symbol in NSE_100:
        print(f"🔍 Processing {symbol}...")
        cmp = fetch_cmp(symbol)
        time.sleep(1)  # Rate limiting to avoid API burst
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
