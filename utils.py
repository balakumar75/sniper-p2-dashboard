"""
utils.py  •  data-fetch, indicators, & helper functions (updated hist_pop)
"""
import time, datetime as dt
import pandas as pd, numpy as np
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ── Kite instance injected at runtime ───────────────────────────────────────
_kite = None
def set_kite(k):
    global _kite
    _kite = k

# ── Date helpers ───────────────────────────────────────────────────────────
def _today():     return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

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
            data = _kite.historical_data(
                token(sym), _days_ago(days), _today(), interval="day"
            )
            df = pd.DataFrame(data)
            return df if not df.empty else None
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None

# ── ATR, ADX, RSI remain unchanged ──────────────────────────────────────────
def atr(df,n=14):
    high_low = df["high"] - df["low"]
    high_cp  = (df["high"] - df["close"].shift()).abs()
    low_cp   = (df["low"]  - df["close"].shift()).abs()
    tr       = pd.concat([high_low,high_cp,low_cp],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def adx(df,n=14):
    up   = df["high"].diff()
    down = (df["low"].diff()*-1)
    plus_dm  = up.where((up>down)&(up>0),0.0)
    minus_dm = down.where((down>up)&(down>0),0.0)
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    atr14 = tr.rolling(n).mean()
    plus_di  = 100 * plus_dm.rolling(n).sum()  / atr14
    minus_di = 100 * minus_dm.rolling(n).sum() / atr14
    dx = (plus_di-minus_di).abs()/(plus_di+minus_di)*100
    return dx.rolling(n).mean()

def rsi(df,n=14):
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    dn   = -diff.clip(upper=0)
    rs   = up.rolling(n).mean()/dn.rolling(n).mean()
    return 100 - 100/(1+rs)

# ── Revised historical PoP helper ──────────────────────────────────────────
def hist_pop(symbol: str, tgt_pct: float, sl_pct: float, lookback_days: int = 90) -> float | None:
    """
    PoP = wins / (wins + losses),
    where wins = days high>=entry*(1+tgt_pct) & low>sl,
          losses = days low<=entry*(1-sl_pct) & high<target,
    ignoring days where neither threshold touched.
    """
    df = fetch_ohlc(symbol, lookback_days+1)
    if df is None or df.empty or len(df) < 2:
        return None

    wins = losses = 0
    for i in range(1, len(df)):
        entry = df["close"].iloc[i-1]
        tgt   = entry * (1 + tgt_pct/100)
        sl    = entry * (1 - sl_pct/100)
        day   = df.iloc[i]
        high, low = day["high"], day["low"]

        hit_tgt = high >= tgt
        hit_sl  = low  <= sl

        if hit_tgt and not hit_sl:
            wins += 1
        elif hit_sl and not hit_tgt:
            losses += 1
        # if both hit or neither hit, ignore this day

    total = wins + losses
    if total == 0:
        return None
    return round(wins / total, 2)

# ── Liquidity helper ────────────────────────────────────────────────────────
def avg_turnover(df: pd.DataFrame, n: int = 20) -> float:
    if df is None or df.empty:
        return 0.0
    turn = (df["close"] * df["volume"]).rolling(n).mean().iloc[-1]
    return round(turn / 1e7, 2)
