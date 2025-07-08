import json
from utils import fetch_cmp, generate_trade_signal
from kiteconnect import KiteConnect
import os

# ✅ Load Access Token
def load_access_token():
    try:
        with open("token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("❌ token.txt file not found.")
        return None

# ✅ Initialize Kite
access_token = load_access_token()
api_key = os.getenv("API_KEY") or "v5h2it4guguvb2pc"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ✅ Define full NSE 100 list
stock_list = [
    "RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", "TCS", "LTIM", "SBIN", "AXISBANK", "ITC", "KOTAKBANK",
    "BAJFINANCE", "BHARTIARTL", "HCLTECH", "ASIANPAINT", "MARUTI", "SUNPHARMA", "NESTLEIND", "TITAN",
    "ULTRACEMCO", "WIPRO", "TECHM", "ADANIENT", "TATASTEEL", "HINDUNILVR", "POWERGRID", "COALINDIA",
    "NTPC", "ONGC", "BRITANNIA", "DIVISLAB", "GRASIM", "JSWSTEEL", "BAJAJFINSV", "CIPLA", "HDFCLIFE",
    "HINDALCO", "BPCL", "EICHERMOT", "SBILIFE", "ICICIPRULI", "DRREDDY", "BAJAJ-AUTO", "HEROMOTOCO",
    "ADANIPORTS", "INDUSINDBK", "TATAMOTORS", "APOLLOHOSP", "PIDILITIND", "DABUR", "GAIL", "HAVELLS",
    "M&M", "SIEMENS", "AMBUJACEM", "SHREECEM", "TORNTPHARM", "DLF", "BIOCON", "TVSMOTOR", "VEDL",
    "LT", "MANAPPURAM", "MUTHOOTFIN", "BANKBARODA", "CANBK", "TRENT", "ZEEL", "IOC", "HINDPETRO",
    "IGL", "RECLTD", "SAIL", "CHOLAFIN", "JINDALSTEL", "SRF", "AUROPHARMA", "LTI", "BOSCHLTD",
    "UNIONBANK"
]

# ✅ Generate Trades
def generate_sniper_trades():
    trades = []
    for stock in stock_list:
        print(f"🔍 Processing {stock}...")
        try:
            cmp = fetch_cmp(kite, stock)
            signal = generate_trade_signal(stock, cmp)
            if signal:
                trades.append(signal)
        except Exception as e:
            print(f"❌ Error processing {stock}: {e}")
    return trades

# ✅ Save to JSON
def save_trades_to_json(trades):
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)

# ✅ Run Combined

def run_sniper_system():
    trades = generate_sniper_trades()
    if trades:
        save_trades_to_json(trades)
        print(f"✅ {len(trades)} trades saved to trades.json")
    else:
        print("⚠️ No trades generated or unexpected result format.")
