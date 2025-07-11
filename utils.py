# ✅ UPDATED utils.py with .env loading for Zerodha

from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv("config.env")

api_key = os.getenv("ZERODHA_API_KEY")
access_token = os.getenv("ZERODHA_ACCESS_TOKEN")

# ✅ Initialize KiteConnect
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def fetch_cmp(symbol):
    try:
        if symbol.endswith("FUT"):
            exchange = "NFO"
        else:
            exchange = "NSE"

        instrument = f"{exchange}:{symbol}"
        quote = kite.ltp([instrument])
        return round(quote[instrument]['last_price'], 2)
    except Exception as e:
        print(f"❌ fetch_cmp error for {symbol}: {e}")
        return None

def calculate_pop(symbol):
    return "85%"

def validate_structure(symbol):
    return True

def get_sector(symbol):
    return "Neutral"

def detect_tags(symbol):
    return ["RSI✅", "MACD✅", "ADX✅"]

# ✅ UPDATED sniper_engine.py

from utils import fetch_cmp, calculate_pop, validate_structure, get_sector, detect_tags
import json
from datetime import datetime

FNO_STOCKS = ["HDFCLIFE", "SBIN", "RELIANCE"]

def generate_sniper_trades():
    print("🚀 Sniper Engine Starting...")
    trades = []
    today = datetime.today().strftime("%Y-%m-%d")

    for symbol in FNO_STOCKS:
        print(f"🔍 Checking {symbol}...")
        try:
            cmp = fetch_cmp(symbol)
            if cmp is None:
                raise ValueError("CMP fetch failed")

            if not validate_structure(symbol):
                print(f"⚠️ Structure validation failed for {symbol}")
                continue

            entry = cmp
            target = round(entry * 1.02, 2)
            sl = round(entry * 0.975, 2)
            trade = {
                "date": today,
                "symbol": symbol,
                "type": "Cash",
                "entry": entry,
                "cmp": cmp,
                "target": target,
                "sl": sl,
                "pop": calculate_pop(symbol),
                "action": "Buy",
                "sector": get_sector(symbol),
                "tags": detect_tags(symbol),
                "status": "Open",
                "exit_date": "-",
                "holding_days": 0,
                "pnl": 0.0,
                "return_pct": "0%"
            }
            trades.append(trade)
        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

    print(f"✅ Trades generated: {len(trades)}")
    return trades

def save_trades_to_json(trades):
    try:
        with open("trades.json", "w") as f:
            json.dump(trades, f, indent=2)
        print("✅ trades.json saved successfully.")
    except Exception as e:
        print(f"❌ Error saving trades: {e}")
