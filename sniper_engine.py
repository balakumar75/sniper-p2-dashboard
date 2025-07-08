import os
import json
import time
from kiteconnect import KiteConnect
from utils import fetch_cmp, generate_trade_signal

kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
kite.set_access_token(os.getenv("KITE_ACCESS_TOKEN"))

NSE_100_STOCKS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "LT", "KOTAKBANK",
    "SBIN", "AXISBANK", "ITC", "BHARTIARTL", "BAJFINANCE", "ASIANPAINT", "HINDUNILVR",
    "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "HCLTECH", "WIPRO", "POWERGRID",
    "NTPC", "INDUSINDBK", "JSWSTEEL", "M&M", "NESTLEIND", "SBILIFE", "TECHM", "UPL",
    "DIVISLAB", "HINDALCO", "TATACONSUM", "TATASTEEL", "TATAMOTORS", "VEDL", "BRITANNIA",
    "DLF", "GAIL", "AMBUJACEM", "ICICIPRULI", "PIDILITIND", "PEL", "SHREECEM", "SIEMENS",
    "TORNTPHARM", "LTI", "LTIM", "HAVELLS", "TVSMOTOR", "SRF", "ABB", "APOLLOHOSP",
    "BOSCHLTD", "AUROPHARMA", "BANKBARODA", "BIOCON", "CANBK", "CHOLAFIN", "HINDPETRO",
    "IGL", "IOC", "JINDALSTEL", "MANAPPURAM", "MUTHOOTFIN", "RECLTD", "SAIL", "TATAPOWER",
    "TRENT", "UNIONBANK", "ZEEL"
]

def generate_sniper_trades():
    trades = []
    for symbol in NSE_100_STOCKS:
        print(f"🔍 Processing {symbol}...")
        try:
            cmp = fetch_cmp(kite, symbol)
            signal = generate_trade_signal(kite, symbol, cmp)
            if signal:
                trades.append(signal)
                print(f"✅ Trade generated: {symbol}")
            else:
                print(f"⏭️ No trade signal for {symbol}")
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
        time.sleep(0.5)  # Sleep between API calls to avoid rate limiting
    return trades

def save_trades_to_json(trades, filename="trades.json"):
    try:
        with open(filename, "w") as f:
            json.dump(trades, f, indent=4)
        print(f"✅ Trades saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving trades: {e}")
