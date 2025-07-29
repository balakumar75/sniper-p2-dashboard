# sector_momentum.py

import pandas as pd
from datetime import date, timedelta
import utils
from config import FNO_SYMBOLS

# simple sector mapping; extend as needed
SECTOR_MAP = {
    "RELIANCE":    "Energy",
    "ONGC":        "Energy",
    "TCS":         "IT",
    "INFY":        "IT",
    "HDFCBANK":    "Banking",
    "ICICIBANK":   "Banking",
    # … add all your FNO_SYMBOLS …
}

def compute_sector_momentum(days: int = 30) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
      sector, avg_return (%), avg_rsi, momentum_rank
    """
    rows = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=days+1)
        if df is None or len(df)<2: continue
        ret = (df["close"].iloc[-1] / df["close"].iloc[0] - 1)*100
        rsi = utils.fetch_rsi(sym, period=14)
        sector = SECTOR_MAP.get(sym, "Other")
        rows.append({"symbol":sym, "sector":sector, "return":ret, "rsi":rsi})
    df = pd.DataFrame(rows)
    agg = df.groupby("sector").agg(
        avg_return = ("return","mean"),
        avg_rsi    = ("rsi","mean"),
        count      = ("symbol","count")
    ).reset_index()
    agg["momentum_rank"] = agg["avg_return"].rank(ascending=False)
    return agg

def top_sectors(n: int = 3) -> list[str]:
    df = compute_sector_momentum()
    return df.nsmallest(n, "momentum_rank")["sector"].tolist()
