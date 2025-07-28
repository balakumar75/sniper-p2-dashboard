# utils.py (top of file)

import datetime
import pandas as pd
import numpy as np

# ── Global Kite client ─────────────────────────────────────────────────────
_kite = None
def set_kite(k):
    global _kite
    _kite = k

def fetch_ohlc(symbol: str, days: int):
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    from instruments import SYMBOL_TO_TOKEN
    token = SYMBOL_TO_TOKEN.get(symbol)
    if not token:
        return None
    data = _kite.historical_data(
        instrument_token=token,
        from_date=(datetime.date.today() - datetime.timedelta(days=days)).isoformat(),
        to_date=datetime.date.today().isoformat(),
        interval="day"
    )
    if not data:
        return None
    df = pd.DataFrame(data).set_index("date")
    return df

# ── Wilder RSI over a long lookback ────────────────────────────────────────
def fetch_rsi(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=100)   # 100 days to let EWM settle
    if df is None or len(df) < period + 1:
        return 0.0
    delta = df["close"].diff().dropna()
    up   = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up   = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs  = ma_up.iloc[-1] / ma_down.iloc[-1] if ma_down.iloc[-1] != 0 else np.inf
    return float(100 - (100 / (1 + rs)))

# ── Wilder ADX over a long lookback ────────────────────────────────────────
def fetch_adx(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=100)   # 100 days for ADX smoothing
    if df is None or len(df) < period * 2:
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

    val = adx.iloc[-1]
    return float(val) if not np.isnan(val) else 0.0

# … leave your other helpers (hist_pop, option_token, etc.) untouched below …
