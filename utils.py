#!/usr/bin/env python3
"""
utils.py

Data‐fetch, indicators, & helpers for options/futures.
Includes:
  • OHLC fetch with retry
  • ATR, ADX, RSI indicators
  • Black‐Scholes delta
  • Stubbed hist_pop for PoP
  • Wrappers: fetch_rsi, fetch_adx, fetch_macd
  • Option & Future token lookups
  • Price fetchers for NFO instruments
"""
import time
import datetime as dt
import math
import pandas as pd
import numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# Kite instance (set by sniper_run_all.py)
_kite = None
def set_kite(k):
    global _kite
    _kite = k

# Date helpers
def _today():     return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

# Instrument lookup
from instruments import SYMBOL_TO_TOKEN, OPTION_TOKENS, FUTURE_TOKENS
def token(sym): return SYMBOL_TO_TOKEN[sym]

# ── OHLC fetch ────────────────────────────────────────────────────────────────
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
        except Exception:
            return None
    return None

# ── INDICATORS ───────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr       = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
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

def rsi(df: pd.DataFrame, n: int = 14) -> pd.Series:
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean() / dn.rolling(n).mean()
    return 100 - 100 / (1 + rs)

# ── HISTORICAL PoP (stub) ─────────────────────────────────────────────────────
def hist_pop(symbol: str, tgt_pct: float, sl_pct: float, lookback_days: int = 90) -> float:
    # stub: pretend every symbol has PoP = 1.0 for testing
    return 1.0

def avg_turnover(df: pd.DataFrame, n: int = 20) -> float:
    if df is None or df.empty:
        return 0.0
    turn = (df["close"] * df["volume"]).rolling(n).mean().iloc[-1]
    return round(turn / 1e7, 2)

# ── BLACK‐SCHOLES DELTA ───────────────────────────────────────────────────────
def norm_cdf(x: float) -> float:
    return (1 + math.erf(x / math.sqrt(2))) / 2

def bs_delta(spot: float, strike: float, dte: int, call: bool = True,
             vol: float = 0.25, r: float = 0.05) -> float:
    t = dte / 365
    d1 = (math.log(spot/strike) + (r + 0.5 * vol**2) * t) / (vol * math.sqrt(t))
    return (math.exp(-r*t) * norm_cdf(d1)) if call else (-math.exp(-r*t) * norm_cdf(-d1))

# ── TOKEN LOOKUPS ────────────────────────────────────────────────────────────
def option_token(symbol: str, strike: int, expiry, option_type: str) -> int:
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return OPTION_TOKENS[symbol][exp_str][option_type].get(strike, 0)

def future_token(symbol: str, expiry) -> int:
    exp_str = expiry if isinstance(expiry, str) else expiry.isoformat()
    return FUTURE_TOKENS[symbol].get(exp_str, 0)

# ── PRICE FETCHERS ───────────────────────────────────────────────────────────
def fetch_option_price(token_id: int) -> float | None:
    if not token_id or _kite is None:
        return None
    key = f"NFO:{token_id}"
    res = _kite.ltp(key)
    return res[key]["last_price"]

def fetch_future_price(token_id: int) -> float | None:
    if not token_id or _kite is None:
        return None
    key = f"NFO:{token_id}"
    res = _kite.ltp(key)
    return res[key]["last_price"]

# ── WRAPPER FETCHERS ─────────────────────────────────────────────────────────
def fetch_rsi(symbol: str, lookback_days: int = 60, n: int = 14) -> float | None:
    df = fetch_ohlc(symbol, lookback_days)
    return None if df is None else rsi(df, n).iloc[-1]

def fetch_adx(symbol: str, lookback_days: int = 60, n: int = 14) -> float | None:
    df = fetch_ohlc(symbol, lookback_days)
    return None if df is None else adx(df, n).iloc[-1]

def fetch_macd(symbol: str, lookback_days: int = 60,
               fast: int = 12, slow: int = 26, signal: int = 9) -> float | None:
    df = fetch_ohlc(symbol, lookback_days)
    if df is None:
        return None
    exp1 = df["close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["close"].ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return hist.iloc[-1]
