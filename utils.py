"""
utils.py  •  data-fetch, indicators, & helper functions (updated with fetch_* wrappers)
"""
import time
import datetime as dt
import pandas as pd
import numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ── Kite instance injected at runtime ───────────────────────────────────────
_kite = None
def set_kite(k):
    global _kite
    _kite = k

# ── Date helpers ───────────────────────────────────────────────────────────
def _today():
    return dt.date.today()

def _days_ago(d):
    return _today() - dt.timedelta(days=d)

# ── Instrument lookup ──────────────────────────────────────────────────────
from instruments import SYMBOL_TO_TOKEN
def token(sym):
    return SYMBOL_TO_TOKEN[sym]

# ── OHLC fetch with retry & rate-limit ─────────────────────────────────────
def fetch_ohlc(sym: str, days: int) -> pd.DataFrame | None:
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    for attempt in range(5):
        gate()
        try:
            raw = _kite.historical_data(
                token(sym),
                _days_ago(days),
                _today(),
                interval="day"
            )
            df = pd.DataFrame(raw)
            return df if not df.empty else None
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None

# ── ATR ─────────────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ── ADX ─────────────────────────────────────────────────────────────────────
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

# ── RSI ─────────────────────────────────────────────────────────────────────
def rsi(df: pd.DataFrame, n: int = 14) -> pd.Series:
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean() / dn.rolling(n).mean()
    return 100 - 100 / (1 + rs)

# ── Historical PoP ──────────────────────────────────────────────────────────
def hist_pop(df: pd.DataFrame, tgt_pct: float, sl_pct: float) -> float | None:
    if df is None or df.empty or len(df) < 2:
        return None
    wins = 0
    trials = len(df) - 1
    for i in range(1, len(df)):
        entry = df["close"].iloc[i - 1]
        tgt   = entry * (1 + tgt_pct/100)
        sl    = entry * (1 - sl_pct/100)
        day   = df.iloc[i]
        if day["high"] >= tgt:
            wins += 1
    return round(wins / trials, 2) if trials > 0 else None

# ── Liquidity helper ────────────────────────────────────────────────────────
def avg_turnover(df: pd.DataFrame, n: int = 20) -> float:
    if df is None or df.empty:
        return 0.0
    turn = (df["close"] * df["volume"]).rolling(n).mean().iloc[-1]
    return round(turn / 1e7, 2)

# ── Wrapper fetch_* functions for backtest.py ────────────────────────────────
def fetch_rsi(symbol: str, days: int = 60) -> float | None:
    df = fetch_ohlc(symbol, days)
    if df is None or df.empty:
        return None
    return rsi(df).iloc[-1]

def fetch_adx(symbol: str, days: int = 60) -> float | None:
    df = fetch_ohlc(symbol, days)
    if df is None or df.empty:
        return None
    return adx(df).iloc[-1]

def fetch_macd(symbol: str, days: int = 90) -> float | None:
    """
    Returns the latest MACD histogram value (EMA12-EMA26 minus signal line).
    """
    df = fetch_ohlc(symbol, days)
    if df is None or df.empty:
        return None
    price = df["close"]
    ema12 = price.ewm(span=12, adjust=False).mean()
    ema26 = price.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal    = macd_line.ewm(span=9, adjust=False).mean()
    hist      = macd_line - signal
    return hist.iloc[-1]
