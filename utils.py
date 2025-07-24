"""
utils.py  •  data-fetch, indicators, & helper functions
"""
import time, datetime as dt
import pandas as pd, numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ── Kite instance is injected at runtime (sniper_run_all.py) ───────────────
_kite = None
def set_kite(k):  # call in sniper_run_all.py
    global _kite
    _kite = k

# ── Date helpers ───────────────────────────────────────────────────────────
def _today():     return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

# ── Instrument mapping ─────────────────────────────────────────────────────
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

# ── Moving average ─────────────────────────────────────────────────────────
def sma(series: pd.Series, n: int = 200) -> pd.Series:
    return series.rolling(n).mean()

# ── Average True Range ─────────────────────────────────────────────────────
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
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
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

# ── Historical PoP (win-rate) ───────────────────────────────────────────────
def hist_pop(df: pd.DataFrame, tgt_pct: float, sl_pct: float, lookback: int = 90) -> float | None:
    if df is None or df.empty or len(df) < 2:
        return None
    wins = 0
    for i in range(1, len(df)):
        entry = df["close"].iloc[i-1]
        tgt   = entry * (1 + tgt_pct/100)
        sl    = entry * (1 - sl_pct/100)
        day   = df.iloc[i]
        # count win if high hits target before low hits SL
        if day["high"] >= tgt and day["low"] > sl:
            wins += 1
    return round(wins / (len(df)-1), 2)

# ── Liquidity (₹ Cr) ────────────────────────────────────────────────────────
def avg_turnover(df: pd.DataFrame, n: int = 20) -> float:
    if df is None or df.empty:
        return 0.0
    turn = (df["close"] * df["volume"]).rolling(n).mean().iloc[-1]
    return round(turn / 1e7, 2)
