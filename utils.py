import pandas as pd
import numpy as np

def fetch_rsi(symbol: str, period: int = 14) -> float:
    """
    Compute Wilder’s RSI over `period` days using EMA smoothing.
    """
    df = fetch_ohlc(symbol, period * 3)
    if df is None or df.empty or len(df) < period + 1:
        return 0.0

    delta = df["close"].diff().dropna()
    up   = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    # Wilder smoothing: alpha = 1/period
    ma_up   = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()

    rs  = ma_up.iloc[-1] / ma_down.iloc[-1] if ma_down.iloc[-1] != 0 else np.inf
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def fetch_adx(symbol: str, period: int = 14) -> float:
    """
    Compute Wilder’s ADX over `period` days using EMA smoothing.
    """
    df = fetch_ohlc(symbol, period * 5)
    if df is None or df.empty or len(df) < period * 2:
        return 0.0

    high, low, close = df["high"], df["low"], df["close"]

    # True Range (TR)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Directional Movement
    up_move   = high.diff()
    down_move = -low.diff()
    plus_dm   = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm  = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    # Wilder smoothing via EMA (alpha=1/period)
    atr       = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di   = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
    minus_di  = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)

    dx        = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx       = dx.ewm(alpha=1/period, adjust=False).mean()

    return float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 0.0
