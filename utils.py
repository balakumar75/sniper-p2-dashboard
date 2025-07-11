from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# 🔐 Load from config.env in root
load_dotenv("config.env")

api_key = os.getenv("ZERODHA_API_KEY")
access_token = os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def fetch_cmp(symbol):
    try:
        if symbol.endswith("FUT"):
            symbol = symbol.replace("FUT", "").strip()
            exchange = "NFO"
            tradingsymbol = f"{symbol}23JULFUT"
        else:
            exchange = "NSE"
            tradingsymbol = symbol

        quote = kite.ltp(f"{exchange}:{tradingsymbol}")
        cmp = quote[f"{exchange}:{tradingsymbol}"]["last_price"]
        return cmp
    except Exception as e:
        print(f"❌ fetch_cmp error for {symbol}: {e}")
        return None
