"""
utils.py

Data-fetch, indicators, & helpers for options/futures.
Includes Black-Scholes delta and expiry handling.
"""
import time
import datetime as dt
import math
import pandas as pd
import numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# Kite instance injected at runtime
_kite = None

def set_kite(k):
    global _kite; _kite = k

# Date helpers
def _today(): return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

# Instrument lookup
from instruments import SYMBOL_TO_TOKEN, OPTION_TOKENS, FUTURE_TOKENS

def token(sym): return SYMBOL_TO_TOKEN[sym]

def fetch_ohlc(sym: str, days: int) -> pd.DataFrame | None:
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    for attempt in range(5):
        gate()
        try:
            data = _kite.historical_data(
                token(sym), _days_ago(days), _today(), interval="day"
            )
            df = pd.DataFrame(data)
            return df if not df.empty else None
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2**attempt)
                continue
            return None
        except:
            return None
    return None

# Indicators
def atr(df, n=14):
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr       = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def adx(df, n=14):
    up   = df["high"].diff()
    down = (df["low"].diff() * -1)
    plus_dm  = up.where((up>down)&(up>0), 0.0)
    minus_dm = down.where((down>up)&(down>0), 0.0)
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr14 = tr.rolling(n).mean()
    plus_di  = 100 * plus_dm.rolling(n).sum()  / atr14
    minus_di = 100 * minus_dm.rolling(n).sum() / atr14
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    return dx.rolling(n).mean()

def rsi(df, n=14):
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean() / dn.rolling(n).mean()
    return 100 - 100 / (1 + rs)

# Historical PoP
def hist_pop(symbol, tgt_pct, sl_pct, lookback_days=90):
    # existing implementation...
    pass

def avg_turnover(df, n=20):
    if df is None or df.empty:
        return 0.0
    turn = (df["close"] * df["volume"]).rolling(n).mean().iloc[-1]
    return round(turn / 1e7, 2)

# Black-Scholes helpers
def norm_cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2

def bs_delta(spot, strike, dte, call=True, vol=0.25, r=0.05):
    t = dte / 365
    d1 = (math.log(spot/strike) + (r + 0.5 * vol**2) * t) / (vol * math.sqrt(t))
    return (math.exp(-r*t) * norm_cdf(d1)) if call else (-math.exp(-r*t) * norm_cdf(-d1))

# New helpers with expiry string handling
def option_token(symbol, strike, expiry, option_type):
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return OPTION_TOKENS[symbol][exp_str][option_type][strike]

def fetch_option_price(token_id):
    res = _kite.ltp(f"NFO:{token_id}")
    return res[f"NFO:{token_id}"]["last_price"]

def future_token(symbol, expiry):
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return FUTURE_TOKENS[symbol][exp_str]

def fetch_future_price(token_id):
    res = _kite.ltp(f"NSE:FUT{token_id}")
    return res[f"NSE:FUT{token_id}"]["last_price"]
