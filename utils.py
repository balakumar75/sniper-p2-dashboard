"""
Utility functions used by Sniper Engine
"""
import time, datetime as dt
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate            # ← NEW

# You already create one global `kite` object in sniper_run_all.py
from sniper_run_all import kite          # reuse same authenticated instance


# ---------------------------------------------------------------------------
# Helpers to calculate date ranges
# ---------------------------------------------------------------------------
def end_date():
    return dt.date.today()

def start_date(days: int):
    return end_date() - dt.timedelta(days=days)

def instrument_token(symbol: str) -> int:
    """
    Look up instrument token for symbol.
    (stub here – replace with your actual lookup or instrument dump)
    """
    from instruments import SYMBOL_TO_TOKEN  # your mapping
    return SYMBOL_TO_TOKEN[symbol]


# ---------------------------------------------------------------------------
# OHLC fetch with retry + rate-limit guard
# ---------------------------------------------------------------------------
def fetch_ohlc(symbol: str, days: int):
    """Return a DataFrame or None when all retries fail."""
    for attempt in range(5):
        gate()                                   # rate limiter
        try:
            return kite.historical_data(
                instrument_token(symbol),
                start_date(days),
                end_date(),
                interval="day"
            )
        except kc_ex.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)         # 1-2-4-8-16 s back-off
                continue
            return None                          # some other Kite error
        except Exception:
            return None                          # network / parse error
    return None


# ---------------------------------------------------------------------------
# RSI helper (safe when OHLC missing)
# ---------------------------------------------------------------------------
def fetch_rsi(symbol: str, n: int = 14):
    """
    Return RSI value or -1 when data unavailable.
    """
    df = fetch_ohlc(symbol, n + 20)
    if df is None or df.empty:
        return -1

    diff = df["close"].diff().dropna()
    up   = diff.where(diff > 0, 0.0)
    down = -diff.where(diff < 0, 0.0)

    roll_up   = up.rolling(n).mean()
    roll_down = down.rolling(n).mean()
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs.iloc[-1]))
    return round(rsi, 2)
