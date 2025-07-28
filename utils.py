# utils.py

import math, datetime
import pandas as pd
import numpy as np

# ── Global Kite client ─────────────────────────────────────────────────────
_kite = None

def set_kite(k):
    """
    Called once from sniper_run_all.py to inject the authenticated KiteConnect
    instance into this module.
    """
    global _kite
    _kite = k

# ── OHLC fetcher ────────────────────────────────────────────────────────────
def fetch_ohlc(symbol: str, days: int):
    """
    Returns a pandas DataFrame of daily OHLC for the last `days` trading sessions.
    Requires that set_kite() has already been called.
    """
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")

    # You'll need to map your symbol → instrument_token in instruments.py
    from instruments import SYMBOL_TO_TOKEN
    token = SYMBOL_TO_TOKEN.get(symbol)
    if not token:
        return None

    # Fetch end‑of‑day bars via KiteConnect
    # NOTE: KiteConnect.historical returns a list of dicts:
    data = _kite.historical_data(
        instrument_token=token,
        from_date=(datetime.date.today() - datetime.timedelta(days=days)).isoformat(),
        to_date=datetime.date.today().isoformat(),
        interval="day"
    )
    if not data:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

# ── RSI & ADX as per Wilder’s EWM formula ──────────────────────────────────
def fetch_rsi(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, period * 3)
    if df is None or len(df) < period+1:
        return 0.0
    delta = df["close"].diff().dropna()
    up   = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up   = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs  = ma_up.iloc[-1] / ma_down.iloc[-1] if ma_down.iloc[-1] != 0 else np.inf
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def fetch_adx(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, period * 5)
    if df is None or len(df) < period*2:
        return 0.0
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    up_move   = high.diff()
    down_move = -low.diff()
    plus_dm   = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm  = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    atr       = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di   = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean()  / atr)
    minus_di  = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
    dx        = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx       = dx.ewm(alpha=1/period, adjust=False).mean()
    return float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 0.0

# ── The rest of your util functions (hist_pop, option_token, etc.) go here ──
