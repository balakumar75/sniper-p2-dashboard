import json
import time
from utils import fetch_cmp, generate_trade_signal

# ✅ Full NSE 100 Stocks List
NSE_100 = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "LT", "KOTAKBANK", "SBIN", "AXISBANK", "ITC",
    "BHARTIARTL", "BAJFINANCE", "ASIANPAINT", "HINDUNILVR", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "HCLTECH", "WIPRO",
    "POWERGRID", "NTPC", "INDUSINDBK", "JSWSTEEL", "M&M", "NESTLEIND", "SBILIFE", "TECHM", "UPL", "DIVISLAB",
    "HINDALCO", "TATACONSUM", "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA", "DLF", "GAIL", "AMBUJACEM", "ICICIPRULI",
    "PIDILITIND", "SHREECEM", "SIEMENS", "LTIM", "HAVELLS", "TVSMOTOR", "SRF", "ABB", "APOLLOHOSP", "BOSCHLTD",
    "AUROPHARMA", "BANKBARODA", "BIOCON", "CANBK", "CHOLAFIN", "HINDPETRO", "IGL", "IOC", "JINDALSTEL", "MANAPPURAM",
    "MUTHOOTFIN", "RECLTD", "SAIL", "TATAPOWER", "TRENT", "UNIONBANK", "ZEEL", "CIPLA", "EICHERMOT", "ADANIENT",
    "GRASIM", "BAJAJ-AUTO", "HEROMOTOCO", "DRREDDY", "COALINDIA", "ADANIPORTS", "DLF", "INDIGO", "BAJAJFINSV", "ICICIGI",
    "NAUKRI", "MPHASIS", "LUPIN", "PEL", "MCDOWELL-N", "COLPAL", "IEX", "GUJGASLTD", "MCX", "IRCTC",
    "IDFCFIRSTB", "INDIAMART", "BANDHANBNK", "ESCORTS", "BEL", "TATACHEM", "ABCAPITAL", "VOLTAS", "HAL", "CUMMINSIND"
]

def generate_sniper_trades():
    trades = []
    for symbol in NSE_100:
        print(f"🔍 Processing {symbol}...")
        cmp = fetch_cmp(symbol)
        time.sleep(0.75)  # ⏱️ Rate limit control for API
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
