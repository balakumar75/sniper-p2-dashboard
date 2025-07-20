"""
utils.py  –  Zerodha helpers
• fetch_cmp
• fetch_ohlc
• fetch_option_chain   (CE/PE lists, ltp_map, days_to_exp)
• NEW  donchian_high_low()  → 20-day highest high / lowest low
"""

import os, math
from datetime import datetime as dt, timedelta
import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ─── Env & Kite ────────────────────────────────────────────────────────────
load_dotenv("config.env", override=False)

API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ─── CMP ───────────────────────────────────────────────────────────────────
def fetch_cmp(symbol: str):
    try:
        quote = kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP error {symbol}: {e}")
        return None

# ─── OHLC helper ───────────────────────────────────────────────────────────
def fetch_ohlc(symbol: str, days: int = 60):
    try:
        end, start = dt.today(), dt.today() - timedelta(days=days*2)
        tok = next(i["instrument_token"] for i in kite.instruments("NSE")
                   if i["tradingsymbol"] == symbol)
        data = kite.historical_data(tok, start, end, "day")
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ OHLC error {symbol}: {e}")
        return None

# ─── NEW: 20-day Donchian Channel ─────────────────────────────────────────
def donchian_high_low(symbol: str, window: int = 20):
    """
    Return (highest_high, lowest_low) over <window> sessions.
    None if OHLC unavailable.
    """
    df = fetch_ohlc(symbol, window + 3)
    if df is None or df.empty: return None, None
    hh = df["high"].iloc[-window:].max()
    ll = df["low"].iloc[-window:].min()
    return hh, ll

# ─── Option-chain fetcher (unchanged except ltp_map & days_to_exp) ────────
def fetch_option_chain(symbol: str):
    try:
        today = dt.today().date()
        nfo = kite.instruments("NFO")

        fut = next(i for i in nfo
                   if i["segment"] == "NFO-FUT" and i["tradingsymbol"].startswith(symbol))
        exp_date = fut["expiry"].date()
        days_to_exp = (exp_date - today).days
        expiry_type = "Weekly" if days_to_exp <= 10 else "Monthly"

        chain = [i for i in nfo if i["name"] == symbol and i["expiry"].date() == exp_date]
        ltp_resp = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])

        ce, pe, ltp_map = [], [], {}
        for ins in chain:
            strike = float(ins["strike"])
            key = f"NFO:{ins['tradingsymbol']}"
            ltp_map[strike] = ltp_resp.get(key, {}).get("last_price", 0)
            (ce if ins["instrument_type"] == "CE" else pe).append(strike)

        return {
            "expiry": expiry_type,
            "days_to_exp": days_to_exp,
            "CE": sorted(set(ce)),
            "PE": sorted(set(pe)),
            "ltp_map": ltp_map
        }
    except Exception as e:
        print(f"❌ Option chain error {symbol}: {e}")
        return None
