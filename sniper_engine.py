import json
import time
from utils import fetch_cmp, generate_trade_signal

# Expanded stock universe (NSE 100 - 96 stocks here)
NSE_100 = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "LT", "KOTAKBANK", "SBIN", "AXISBANK", "ITC",
    "BHARTIARTL", "BAJFINANCE", "ASIANPAINT", "HINDUNILVR", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO",
    "HCLTECH", "WIPRO", "POWERGRID", "NTPC", "INDUSINDBK", "JSWSTEEL", "M&M", "NESTLEIND", "SBILIFE",
    "TECHM", "UPL", "DIVISLAB", "HINDALCO", "TATACONSUM", "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA",
    "DLF", "GAIL", "AMBUJACEM", "ICICIPRULI", "PIDILITIND", "BANKBARODA", "ADANIENT", "ADANIPORTS",
    "INDIGO", "DMART", "PNB", "COALINDIA", "CANBK", "SHREECEM", "TRENT", "INDHOTEL", "TVSMOTOR", "CIPLA",
    "ONGC", "BPCL", "NAUKRI", "PAYTM", "BIOCON", "BOSCHLTD", "IRCTC", "MCX", "HINDPETRO", "GUJGASLTD",
    "ZEEL", "IEX", "COLPAL", "CUMMINSIND", "LTI", "LTTS", "TORNTPHARM", "BHEL", "ABFRL", "POLYCAB", "BEL",
    "ESCORTS", "SRF", "CHOLAFIN", "HAL", "INDIAMART", "IDFCFIRSTB", "MUTHOOTFIN", "BANDHANBNK",
    "DEEPAKNTR", "RECLTD", "POWERINDIA", "SJVN", "MAZDOCK", "IRFC", "NHPC", "NBCC", "HUDCO", "RVNL"
]

def generate_sniper_trades():
    trades = []
    for symbol in NSE_100:
        print(f"🔍 Processing {symbol}...")
        cmp = fetch_cmp(symbol)
        time.sleep(0.8)  # Reduced delay for efficiency (within rate limits)
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
