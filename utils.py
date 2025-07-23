import time, datetime as dt
import pandas as pd, numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# kite object is injected once at runtime (sniper_run_all.py)
_kite = None
def set_kite(k):  # called in sniper_run_all
    global _kite
    _kite = k

# ───────────── basic helpers ─────────────
def _now(): return dt.date.today()
def _ago(days): return _now() - dt.timedelta(days=days)

from instruments import SYMBOL_TO_TOKEN
def token(sym): return SYMBOL_TO_TOKEN[sym]

# ───────────── fetch OHLC with retry ─────
def fetch_ohlc(sym: str, days: int):
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not yet called")

    for a in range(5):
        gate()
        try:
            raw = _kite.historical_data(token(sym), _ago(days), _now(), "day")
            df  = pd.DataFrame(raw)
            return df if not df.empty else None
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** a); continue
            return None
        except Exception: return None
    return None

# ───────────── indicator calcs ───────────
def sma(series, n=200): return series.rolling(n).mean()

def atr(df, n=14):
    tr  = pd.concat([
        (df["high"] - df["low"]),
        (df["high"] - df["close"].shift()).abs(),
        (df["low"]  - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def adx(df, n=14):
    up  = df["high"].diff()
    dn  = df["low"].diff().abs()
    plus  = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr   = pd.concat([
        (df["high"] - df["low"]),
        (df["high"] - df["close"].shift()).abs(),
        (df["low"]  - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    atr14 = tr.rolling(n).mean()
    plus_di  = 100 * pd.Series(plus).rolling(n).sum()  / atr14
    minus_di = 100 * pd.Series(minus).rolling(n).sum() / atr14
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    return dx.rolling(n).mean()

def rsi(df, n=14):
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean() / dn.rolling(n).mean()
    return 100 - 100 / (1 + rs)

def hist_pop(df, tgt_pct, sl_pct):
    wins = 0
    for i in range(1, len(df)):
        entry = df["close"].iloc[i-1]
        tgt   = entry * (1 + tgt_pct/100)
        sl    = entry * (1 - sl_pct/100)
        day   = df.iloc[i]
        if day["high"] >= tgt: wins += 1
        elif day["low"] <= sl: pass
    return round(wins / (len(df)-1), 2) if len(df) > 1 else None
