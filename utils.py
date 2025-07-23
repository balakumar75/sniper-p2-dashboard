"""
Utility functions used by Sniper Engine
"""
import time, datetime as dt
import pandas as pd                    # ← NEW
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate

# ---------------------------------------------------------------------------
# Kite instance is injected at runtime (sniper_run_all.py calls utils.set_kite)
# ---------------------------------------------------------------------------
_kite = None

def set_kite(kite_obj):
    global _kite
    _kite = kite_obj

# ---------------------------------------------------------------------------
# Helpers to calculate date ranges
# ---------------------------------------------------------------------------
def end_date():
    return dt.date.today()

def start_date(days: int):
    return end_date() - dt.timedelta(days=days)

def instrument_token(symbol: str) -> int:
    from instruments import SYMBOL_TO_TOKEN
    return SYMBOL_TO_TOKEN[symbol]

# ---------------------------------------------------------------------------
# OHLC fetch with retry + rate-limit guard
# ---------------------------------------------------------------------------
def fetch_ohlc(symbol: str, days: int):
    """Return a pandas DataFrame or None when retries exhaust."""
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")

    for attempt in range(5):
        gate()
        try:
            raw = _kite.historical_data(
                instrument_token(symbol),
                start_date(days),
                end_date(),
                interval="day"
            )
            return pd.DataFrame(raw)   # ← convert list → DataFrame
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None

# ---------------------------------------------------------------------------
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
