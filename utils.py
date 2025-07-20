"""
utils.py – Zerodha helpers
• fetch_cmp
• fetch_* indicators
• NEW  fetch_option_chain  → returns CE, PE strike lists + LTP map + expiry info
"""

import os, math, statistics, datetime
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
import pandas as pd
from kiteconnect import KiteConnect

# ── env & Kite init ───────────────────────────────────────────────────────
load_dotenv("config.env", override=False)

API_KEY       = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN  = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ── CMP (unchanged) ───────────────────────────────────────────────────────
def fetch_cmp(symbol):
    try:
        quote = kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP error {symbol}: {e}")
        return None

# ── OHLC for indicators ───────────────────────────────────────────────────
def fetch_ohlc(symbol, days=60):
    try:
        end = dt.today()
        start = end - timedelta(days=days*2)
        inst = next(i["instrument_token"] for i in kite.instruments("NSE")
                    if i["tradingsymbol"] == symbol)
        data = kite.historical_data(inst, start, end, "day")
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ OHLC error {symbol}: {e}")
        return None

# (RSI, ADX, MACD, Volume helpers as you already have)

# ── NEW: Option-chain fetcher ─────────────────────────────────────────────
def fetch_option_chain(symbol):
    """
    Returns dict:
    {
      'expiry': 'Weekly' | 'Monthly',
      'days_to_exp': int,
      'CE': [strike1,…],
      'PE': [strike1,…],
      'ltp_map': {strike: ltp, …}
    }
    """
    try:
        # 1) find nearest monthly expiry (simplified)
        today = dt.today().date()
        all_instruments = kite.instruments("NFO")
        fut = next(i for i in all_instruments
                   if i["segment"] == "NFO-FUT" and i["tradingsymbol"].startswith(symbol))
        expiry_date = fut["expiry"].date()
        days_to_exp = (expiry_date - today).days
        expiry_type = "Weekly" if days_to_exp <= 10 else "Monthly"

        # 2) pull all opt instruments for this expiry
        chain = [i for i in all_instruments
                 if i["name"] == symbol and i["expiry"].date() == expiry_date]

        ce_list, pe_list, ltp_map = [], [], {}
        ltp_resp = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])
        for ins in chain:
            strike = float(ins["strike"])
            ins_key = f"NFO:{ins['tradingsymbol']}"
