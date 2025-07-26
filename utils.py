#!/usr/bin/env python3
"""
utils.py

Data‐fetch, indicators, & helpers for options/futures.
Includes Black‐Scholes, PoP (stubbed), and fetch_* wrappers.
"""
import time
import datetime as dt
import math
import pandas as pd
import numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

_kite = None
def set_kite(k): 
    global _kite; _kite = k

def _today():     return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

from instruments import SYMBOL_TO_TOKEN, OPTION_TOKENS, FUTURE_TOKENS
def token(sym): return SYMBOL_TO_TOKEN[sym]

def fetch_ohlc(sym: str, days: int) -> pd.DataFrame | None:
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    for _ in range(3):
        gate()
        try:
            data = _kite.historical_data(token(sym), _days_ago(days), _today(), interval="day")
            df = pd.DataFrame(data)
            return df if not df.empty else None
        except:
            time.sleep(1)
    return None

# Indicators omitted for brevity (keep your existing atr/adx/rsi/etc.)

def hist_pop(symbol, tgt_pct, sl_pct, lookback_days=90):
    # stub: pretend every symbol has 100% PoP
    return 1.0

def avg_turnover(df, n=20):
    if df is None or df.empty:
        return 0.0
    return round((df["close"] * df["volume"]).rolling(n).mean().iloc[-1] / 1e7, 2)

def norm_cdf(x): return (1 + math.erf(x / math.sqrt(2))) / 2
def bs_delta(spot, strike, dte, call=True, vol=0.25, r=0.05):
    t = dte / 365
    d1 = (math.log(spot/strike) + (r + 0.5*vol**2)*t) / (vol*math.sqrt(t))
    return (math.exp(-r*t)*norm_cdf(d1)) if call else (-math.exp(-r*t)*norm_cdf(-d1))

def option_token(symbol, strike, expiry, option_type):
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return OPTION_TOKENS[symbol][exp_str][option_type].get(strike, 0)

def future_token(symbol, expiry):
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return FUTURE_TOKENS[symbol].get(exp_str, 0)

def fetch_option_price(tkn):
    if not tkn: return None
    key = f"NFO:{tkn}"
    res = _kite.ltp(key); return res[key]["last_price"]

def fetch_future_price(tkn):
    if not tkn: return None
    key = f"NFO:{tkn}"
    res = _kite.ltp(key); return res[key]["last_price"]

def fetch_rsi(symbol, days=60, n=14):
    df = fetch_ohlc(symbol, days)
    return None if df is None else rsi(df, n).iloc[-1]

# (Include your rsi/atr/adx implementations as before)
