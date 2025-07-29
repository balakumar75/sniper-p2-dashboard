# ict_signals.py

import pandas as pd
import numpy as np
from datetime import timedelta

def detect_fvg(symbol: str, lookback: int = 5) -> list[tuple]:
    """
    Returns list of (start_price, end_price) gaps where
    today's low > yesterday's high AND tomorrow's high < yesterday's low.
    Simplest 3-bar gap.
    """
    from utils import fetch_ohlc
    df = fetch_ohlc(symbol, days=lookback+2)
    if df is None or len(df)<3: return []

    gaps = []
    for i in range(1, len(df)-1):
        prev, curr, nxt = df.iloc[i-1], df.iloc[i], df.iloc[i+1]
        if curr["low"] > prev["high"] and nxt["high"] < prev["low"]:
            gaps.append((prev["high"], prev["low"]))
    return gaps

def detect_order_blocks(symbol: str, lookback: int = 20) -> list[tuple]:
    """
    Returns list of bullish/bearish order‑block zones. 
    E.g., look for inside bars after trending move.
    """
    from utils import fetch_ohlc
    df = fetch_ohlc(symbol, days=lookback)
    if df is None or len(df)<5: return []

    blocks = []
    # naive: any inside bar
    for i in range(2, len(df)):
        if (df["high"].iloc[i] < df["high"].iloc[i-1] and 
            df["low"].iloc[i]  > df["low"].iloc[i-1]):
            # inside bar found
            blocks.append((df["high"].iloc[i], df["low"].iloc[i]))
    return blocks

def detect_structure_shift(symbol: str, lookback: int = 30) -> bool:
    """
    Returns True if market structure flips (HH → LL or LL → HH)
    in the last lookback days.
    """
    from utils import fetch_ohlc
    df = fetch_ohlc(symbol, days=lookback)
    if df is None or len(df)<3: return False

    highs = df["high"]
    lows  = df["low"]
    # is last high < prior high AND last low < prior low → bearish shift
    if highs.iloc[-1] < highs.iloc[-2] and lows.iloc[-1] < lows.iloc[-2]:
        return True
    # bullish shift
    if highs.iloc[-1] > highs.iloc[-2] and lows.iloc[-1] > lows.iloc[-2]:
        return True
    return False
