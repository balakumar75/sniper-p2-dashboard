import json
from utils import fetch_cmp, generate_trade_signal

# NSE 100 stock universe (truncated example — expand as needed)
STOCK_LIST = [
    "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK", "LT", "SBIN", "KOTAKBANK",
    "BHARTIARTL", "ASIANPAINT", "ITC", "AXISBANK", "BAJFINANCE", "HCLTECH", "WIPRO",
    "MARUTI", "TITAN", "ULTRACEMCO", "HINDUNILVR", "ONGC", "POWERGRID", "NTPC", "ADANIENT",
    "ADANIPORTS", "BAJAJFINSV", "BPCL", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
    "GRASIM", "HDFCLIFE", "HEROMOTOCO", "INDUSINDBK", "JSWSTEEL", "M&M", "NESTLEIND",
    "SBILIFE", "SUNPHARMA", "TECHM", "UPL", "DIVISLAB", "HINDALCO", "TATACONSUM",
    "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA", "DLF", "GAIL", "AMBUJACEM",
    "ICICIPRULI", "PIDILITIND", "PEL", "SHREECEM", "SIEMENS", "TORNTPHARM", "LTI",
    "LTIM", "HAVELLS", "TVSMOTOR", "SRF", "ABB", "APOLLOHOSP", "BOSCHLTD", "AUROPHARMA",
    "BANKBARODA", "BIOCON", "CANBK", "CHOLAFIN", "HINDPETRO", "IGL", "IOC", "JINDALSTEL",
    "MANAPPURAM", "MUTHOOTFIN", "RECLTD", "SAIL", "TATAPOWER", "TRENT", "UNIONBANK", "ZEEL"
]

def generate_sniper_trades():
    trades = []

    for symbol in STOCK_LIST:
        try:
            print(f"🔍 Processing {symbol}...")
            cmp = fetch_cmp(symbol)
            trade = generate_trade_signal(symbol, cmp)
            if trade:
                trades.append(trade)
        except Exception as e:
            print(f"❌ Error processing {symbol}: {str(e)}")

    return trades

def save_trades_to_json(trades, output_file="trades.json"):
    with open(output_file, "w") as f:
        json.dump(trades, f, indent=2)
    print(f"✅ Saved {len(trades)} trades to {output_file}")
