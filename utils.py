"""
Utility functions shared by Sniper Engine
"""
import time, datetime as dt
import pandas as pd
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ── Kite instance is injected at runtime ───────────────────────────────────
_kite = None
def set_kite(kite_obj):
    global _kite
    _kite = kite_obj

# ── Date helpers ───────────────────────────────────────────────────────────
def end_date():
    return dt.date.today()

def start_date(days: int):
    return end_date() - dt.timedelta(days=days)

def instrument_token(symbol: str) -> int:
    from instruments import SYMBOL_TO_TOKEN
    return SYMBOL_TO_TOKEN[symbol]

# ── OHLC fetch with retry & rate-limit ─────────────────────────────────────
def fetch_ohlc(symbol: str, days: int):
    """Return pandas DataFrame or None when retries exhaust."""
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")

    for attempt in range(5):
        gate()
        try:
            raw = _kite.historical_data(
                instrument_token(symbol),
                start_date(days),
                end_date(),
                interval="day",
            )
            return pd.DataFrame(raw)
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None

# ── RSI helper ─────────────────────────────────────────────────────────────
def fetch_rsi(symbol: str, n: int = 14):
    df = fetch_ohlc(symbol, n + 20)
    if df is None or df.empty:
        return -1
    diff = df["close"].diff().dropna()
    up   = diff.where(diff > 0, 0.0)
    down = -diff.where(diff < 0, 0.0)
    roll_up   = up.rolling(n).mean()
    roll_down = down.rolling(n).mean()
    rs  = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs.iloc[-1]))
    return round(rsi, 2)

# ── Historical PoP helper ──────────────────────────────────────────────────
def hist_pop(symbol: str, tgt_pct: float, sl_pct: float, lookback_days: int = 90):
    """
    Crude probability-of-profit: % of days in `lookback_days` where
    next day's high hit +tgt_pct *before* low hit -sl_pct.
    Returns a float 0-1 or None if OHLC unavailable.
    """
    df = fetch_ohlc(symbol, lookback_days + 1)
    if df is None or df.empty:
        return None

    wins = 0
    trials = len(df) - 1
    for i in range(1, len(df)):
        entry = df["close"].iloc[i - 1]
        tgt   = entry * (1 + tgt_pct / 100)
        sl    = entry * (1 - sl_pct  / 100)
        day   = df.iloc[i]
        if day["high"] >= tgt:
            wins += 1
        elif day["low"] <= sl:
            pass  # SL first
        else:
            pass  # neither hit
    return round(wins / trials, 2) if trials else None
