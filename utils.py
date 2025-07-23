"""
utils.py  •  shared data‐fetch and indicator functions
"""
import time, datetime as dt
import pandas as pd, numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ── Kite instance is injected at runtime (sniper_run_all.py) ───────────────
_kite = None
def set_kite(k):
    global _kite
    _kite = k

# ── Date helpers ───────────────────────────────────────────────────────────
def _now(): return dt.date.today()
def _ago(days): return _now() - dt.timedelta(days=days)

# ── Instrument lookup ──────────────────────────────────────────────────────
from instruments import SYMBOL_TO_TOKEN
def token(sym): return SYMBOL_TO_TOKEN[sym]

# ── OHLC fetch with retry & rate-limit ─────────────────────────────────────
def fetch_ohlc(sym: str, days: int) -> pd.DataFrame | None:
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")

    for attempt in range(5):
        gate()
        try:
            raw = _kite.historical_data(
                token(sym),
                _ago(days),
                _now(),
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

# ── Moving average ─────────────────────────────────────────────────────────
def sma(series: pd.Series, n: int = 200) -> pd.Series:
    return series.rolling(n).mean()

# ── ATR ─────────────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ── ADX ─────────────────────────────────────────────────────────────────────
def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    up  = df["high"].diff()
    dn  = df["low"].diff().abs()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus= np.where((dn > up) & (dn > 0), dn, 0.0)
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    atr14 = tr.rolling(n).mean()
    plus_di  = 100 * pd.Series(plus).rolling(n).sum()  / atr14
    minus_di = 100 * pd.Series(minus).rolling(n).sum() / atr14
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    return dx.rolling(n).mean()

# ── RSI ─────────────────────────────────────────────────────────────────────
def rsi(df: pd.DataFrame, n: int = 14) -> pd.Series:
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean() / dn.rolling(n).mean()
    return 100 - 100 / (1 + rs)

# ── Historical PoP (for stocks) ─────────────────────────────────────────────
def hist_pop(df: pd.DataFrame, tgt_pct: float, sl_pct: float) -> float | None:
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
