import numpy as np
import pandas as pd
import datetime

# … your existing set_kite, fetch_ohlc, fetch_rsi, fetch_adx, etc. …

def fetch_atr(symbol: str, period: int = 14) -> float:
    """
    Compute a simple ATR over `period` days using rolling mean of True Range.
    """
    df = fetch_ohlc(symbol, days=period*3)
    if df is None or len(df) < period+1:
        return 0.0

    high = df["high"]
    low  = df["low"]
    close= df["close"]
    prev = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev).abs()
    tr3 = (low  - prev).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    val = atr.iloc[-1]
    return float(val) if not np.isnan(val) else 0.0
