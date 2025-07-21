"""
utils.py  –  Zerodha helpers + indicators
• fetch_cmp
• fetch_ohlc
• donchian_high_low
• NEW  in_squeeze_breakout  (TTM-style 20-bar squeeze filter)
• fetch_option_chain  (CE/PE strike lists, ltp_map, days_to_exp)
"""

import os, math
from datetime import datetime as dt, timedelta
import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ── Environment & Kite initialisation ────────────────────────────────────
load_dotenv("config.env", override=False)
API_KEY      = os.getenv("KITE_API_KEY") or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ── 1. CMP ───────────────────────────────────────────────────────────────
def fetch_cmp(symbol: str):
    try:
        quote = kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP error {symbol}: {e}")
        return None

# ── 2. OHLC helper ───────────────────────────────────────────────────────
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

# ── 3. 20-day Donchian Channel ──────────────────────────────────────────
def donchian_high_low(symbol: str, window: int = 20):
    df = fetch_ohlc(symbol, window + 3)
    if df is None or df.empty: return None, None
    return df["high"].iloc[-window:].max(), df["low"].iloc[-window:].min()

# ── 4.  TTM-style squeeze breakout filter ───────────────────────────────
def in_squeeze_breakout(symbol: str,
                        window: int = 20,
                        squeeze_bars: int = 5) -> bool:
    """
    Return True if the *latest* bar is the FIRST close above the upper
    Bollinger Band after <squeeze_bars> consecutive squeeze bars.
    Squeeze = BB(20,2) completely inside KC(20,1.5 ATR).
    """
    df = fetch_ohlc(symbol, window + squeeze_bars + 5)
    if df is None or len(df) < window + squeeze_bars:
        return False

    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values

    # ---- Bollinger Bands (SMA + 2 σ)
    sma = pd.Series(close).rolling(window).mean()
    std = pd.Series(close).rolling(window).std()
    bb_up = sma + 2 * std
    bb_dn = sma - 2 * std

    # ---- Keltner Channel (EMA ± 1.5 ATR)
    ema = pd.Series(close).ewm(span=window, adjust=False).mean()
    tr  = pd.Series(high - low).rolling(window).mean()
    kc_up = ema + 1.5 * tr
    kc_dn = ema - 1.5 * tr

    # past <squeeze_bars> must be in squeeze
    sq = (bb_up[-squeeze_bars:] < kc_up[-squeeze_bars:]) & \
         (bb_dn[-squeeze_bars:] > kc_dn[-squeeze_bars:])
    if not sq.all():                       # need consecutive squeeze bars
        return False

    # breakout on latest bar
    return close[-1] > bb_up.iloc[-1]

# ── 5. Option-chain fetcher (incl. ltp_map & days_to_exp) ────────────────
def fetch_option_chain(symbol: str):
    """
    Returns:
      {
        'expiry':       'Weekly' | 'Monthly',
        'days_to_exp':  int,
        'CE':           [strike1, …],
        'PE':           [strike1, …],
        'ltp_map':      {strike: ltp_price, …}
      }
    """
    try:
        today = dt.today().date()
        nfo   = kite.instruments("NFO")

        fut = next(i for i in nfo
                   if i["segment"] == "NFO-FUT"
                   and i["tradingsymbol"].startswith(symbol))
        exp  = fut["expiry"].date()
        days = (exp - today).days
        exp_type = "Weekly" if days <= 10 else "Monthly"

        chain = [i for i in nfo if i["name"] == symbol and i["expiry"].date() == exp]
        ltp   = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])

        ce, pe, ltp_map = [], [], {}
        for ins in chain:
            strike = float(ins["strike"])
            price  = ltp.get(f"NFO:{ins['tradingsymbol']}", {}).get("last_price", 0)
            ltp_map[strike] = price
            (ce if ins["instrument_type"] == "CE" else pe).append(strike)

        return {
            "expiry": exp_type, "days_to_exp": days,
            "CE": sorted(set(ce)), "PE": sorted(set(pe)),
            "ltp_map": ltp_map
        }

    except Exception as e:
        print(f"❌ OC error {symbol}: {e}")
        return None
