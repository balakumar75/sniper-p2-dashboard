import time
from utils import fetch_cmp, generate_trade_signal

# List of NSE 100 stocks (shortened example; use your full list)
nse_100_stocks = [
    "RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", "TCS", "LTIM", "SBIN", "AXISBANK",
    "ITC", "KOTAKBANK", "BAJFINANCE", "BHARTIARTL", "HCLTECH", "ASIANPAINT", "MARUTI",
    "SUNPHARMA", "NESTLEIND", "TITAN", "ULTRACEMCO", "WIPRO", "TECHM", "ADANIENT",
    "TATASTEEL", "HINDUNILVR", "POWERGRID", "COALINDIA", "NTPC", "ONGC", "BRITANNIA",
    "DIVISLAB", "GRASIM", "JSWSTEEL", "BAJAJFINSV", "CIPLA", "HDFCLIFE", "HINDALCO",
    "BPCL", "EICHERMOT", "SBILIFE", "ICICIPRULI", "DRREDDY", "BAJAJ-AUTO", "HEROMOTOCO",
    "ADANIPORTS", "INDUSINDBK", "TATAMOTORS", "APOLLOHOSP", "PIDILITIND", "DABUR",
    "GAIL", "HAVELLS", "M&M", "SIEMENS", "AMBUJACEM", "SHREECEM", "TORNTPHARM", "DLF",
    "BIOCON", "TVSMOTOR", "VEDL", "LT", "MANAPPURAM", "MUTHOOTFIN", "BANKBARODA",
    "CANBK", "TRENT", "ZEEL", "IOC", "HINDPETRO", "IGL", "RECLTD", "SAIL", "CHOLAFIN",
    "JINDALSTEL", "SRF", "AUROPHARMA", "LTI", "BOSCHLTD", "UNIONBANK"
]

def generate_sniper_trades():
    trades = []
    for symbol in nse_100_stocks:
        try:
            print(f"🔍 Processing {symbol}...")
            cmp = fetch_cmp(symbol)
            if cmp is None:
                print(f"❌ Skipping {symbol} due to CMP fetch error.")
                continue
            trade = generate_trade_signal(symbol, cmp)
            if trade:
                trades.append(trade)
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
        time.sleep(0.4)  # ⏳ Sleep added to avoid rate limits

    return trades
