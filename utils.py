# utils.py

import os
import math
import json
import requests
import pandas as pd
from datetime import date, datetime, timedelta
from scipy.stats import norm

# ── 0) Kite instance (injected via set_kite) ───────────────────────────────

_kite = None

def set_kite(kite):
    global _kite
    _kite = kite

# ── 1) Fetch OHLC candles from Kite ────────────────────────────────────────

def fetch_ohlc(symbol: str, days: int = 30, interval: str = "day") -> pd.DataFrame:
    """
    Returns a DataFrame with columns ['date','open','high','low','close','volume']
    for the past `days`. Requires set_kite(kite) to have been called.
    """
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    # instruments.py defines SYMBOL_TO_TOKEN
    from instruments import SYMBOL_TO_TOKEN
    token = SYMBOL_TO_TOKEN.get(symbol, 0)
    if not token:
        return pd.DataFrame()  # no token → empty

    to_dt   = date.today()
    from_dt = to_dt - timedelta(days=days)
    data = _kite.historical(
        instrument_token=token,
        from_date=from_dt.isoformat(),
        to_date=to_dt.isoformat(),
        interval=interval
    )
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.rename(columns={
        "date":   "date",
        "open":   "open",
        "high":   "high",
        "low":    "low",
        "close":  "close",
        "volume": "volume"
    })
    # ensure chronological order
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)

# ── 2) RSI ──────────────────────────────────────────────────────────────────

def fetch_rsi(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=period*3)
    if df.empty or len(df) < period:
        return 0.0
    delta = df["close"].diff()
    up    = delta.clip(lower=0)
    down  = -delta.clip(upper=0)
    ma_up   = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs    = ma_up / ma_down
    rsi   = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

# ── 3) ADX ─────────────────────────────────────────────────────────────────

def fetch_adx(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=period*3)
    if df.empty or len(df) < period+1:
        return 0.0
    high, low, close = df["high"], df["low"], df["close"]
    plus_dm  = high.diff().where(lambda x: x>low.diff(), 0.0).clip(lower=0)
    minus_dm = low.diff().where(lambda x: x>high.diff(), 0.0).clip(lower=0)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low  - close.shift()).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    plus_di  = 100*(plus_dm.ewm(span=period).mean()/atr)
    minus_di = 100*(minus_dm.ewm(span=period).mean()/atr)
    dx = 100*((plus_di-minus_di).abs()/(plus_di+minus_di))
    adx = dx.ewm(span=period).mean()
    return float(adx.iloc[-1])

# ── 4) ATR ─────────────────────────────────────────────────────────────────

def fetch_atr(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=period*3)
    if df.empty or len(df) < period:
        return 0.0
    high, low, close = df["high"], df["low"], df["close"]
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low  - close.shift()).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return float(atr.iloc[-1])

# ── 5) Historic PoP (proxy) ────────────────────────────────────────────────

def hist_pop(symbol: str, tgt_pct: float, sl_pct: float) -> float:
    """
    Simple proxy: how often in last N days did a ±tgt_pct move NOT hit ±sl_pct first?
    """
    df = fetch_ohlc(symbol, days=60)
    if df.empty:
        return 0.0
    wins = 0
    total = 0
    for i in range(1, len(df)):
        base = df["close"].iloc[i-1]
        high = df["high"].iloc[i]
        low  = df["low"].iloc[i]
        if (high - base)/base*100 >= tgt_pct:
            wins += 1
        total += 1
    return float(wins/total*100) if total else 0.0

# ── 6) MACD ────────────────────────────────────────────────────────────────

def fetch_macd(symbol: str, fast: int = 12, slow: int = 26, signal: int = 9):
    df = fetch_ohlc(symbol, days=slow*3)
    if df.empty:
        return 0.0, 0.0, 0.0
    ema_fast   = df["close"].ewm(span=fast,  adjust=False).mean()
    ema_slow   = df["close"].ewm(span=slow,  adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    sig_line   = macd_line.ewm(span=signal, adjust=False).mean()
    hist       = macd_line - sig_line
    return float(macd_line.iloc[-1]), float(sig_line.iloc[-1]), float(hist.iloc[-1])

# ── 7) Option / future price helpers ───────────────────────────────────────
# (if you have functions like fetch_future_price / option_token etc.)

# ── 8) Black–Scholes Greeks ────────────────────────────────────────────────

def _bs_d1(S, K, r, sigma, T):
    return (math.log(S/K) + (r + 0.5*sigma*sigma)*T)/(sigma*math.sqrt(T))

def _bs_d2(d1, sigma, T):
    return d1 - sigma*math.sqrt(T)

def bs_delta(S, K, r, sigma, expiry, is_call=True):
    T = max(0, (date.fromisoformat(expiry)-date.today()).days/365)
    if T<=0 or sigma<=0: return 0.0
    d1 = _bs_d1(S,K,r,sigma,T)
    return float(norm.cdf(d1) if is_call else (norm.cdf(d1)-1))

def bs_gamma(S, K, r, sigma, expiry):
    T = max(0, (date.fromisoformat(expiry)-date.today()).days/365)
    if T<=0 or sigma<=0: return 0.0
    d1 = _bs_d1(S,K,r,sigma,T)
    return float(norm.pdf(d1)/(S*sigma*math.sqrt(T)))

def bs_vega(S, K, r, sigma, expiry):
    T = max(0, (date.fromisoformat(expiry)-date.today()).days/365)
    if T<=0 or sigma<=0: return 0.0
    d1 = _bs_d1(S,K,r,sigma,T)
    return float(S*norm.pdf(d1)*math.sqrt(T)/100)

def bs_theta(S, K, r, sigma, expiry, is_call=True):
    T = max(0, (date.fromisoformat(expiry)-date.today()).days/365)
    if T<=0 or sigma<=0: return 0.0
    d1 = _bs_d1(S,K,r,sigma,T); d2 = _bs_d2(d1,sigma,T)
    pdf = norm.pdf(d1)
    term1 = -S*pdf*sigma/(2*math.sqrt(T))
    if is_call:
        term2 = r*K*math.exp(-r*T)*norm.cdf(d2)
        return float((term1-term2)/365)
    else:
        term2 = r*K*math.exp(-r*T)*norm.cdf(-d2)
        return float((term1+term2)/365)

def bs_rho(S, K, r, sigma, expiry, is_call=True):
    T = max(0, (date.fromisoformat(expiry)-date.today()).days/365)
    if T<=0 or sigma<=0: return 0.0
    d2 = _bs_d2(_bs_d1(S,K,r,sigma,T), sigma, T)
    if is_call:
        return float(K*T*math.exp(-r*T)*norm.cdf(d2)/100)
    else:
        return float(-K*T*math.exp(-r*T)*norm.cdf(-d2)/100)
