# utils.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Global Kite Connect client placeholder
_kite = None

def set_kite(kite_client):
    """
    Initialize the global Kite Connect client for all data fetch functions.
    """
    global _kite
    _kite = kite_client


def fetch_ohlc(symbol: str, days: int) -> pd.DataFrame:
    """
    Fetch historical OHLC data for the given symbol over the past `days` days using Kite Connect.
    Returns a DataFrame indexed by date with columns ['open','high','low','close','volume'].
    """
    if _kite is None:
        raise RuntimeError("Kite client not set. Call set_kite() first.")
    instrument = f"NSE:{symbol}"
    # Get instrument token from LTP response
    data = _kite.ltp([instrument])
    token = data[instrument]['instrument_token']

    to_date   = datetime.now()
    from_date = to_date - timedelta(days=days)

    # Fetch daily candles
    raw = _kite.historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval="day"
    )
    df = pd.DataFrame(raw)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df[['open','high','low','close','volume']]


def fetch_rsi(symbol: str, period: int) -> float:
    """
    Calculate the period-day RSI for the symbol using fetched OHLC.
    """
    df = fetch_ohlc(symbol, days=period * 3)
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)


def fetch_adx(symbol: str, period: int) -> float:
    """
    Calculate the period-day ADX for the symbol.
    """
    df = fetch_ohlc(symbol, days=period * 3)
    df['high_prev'] = df['high'].shift(1)
    df['low_prev']  = df['low'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - df['close'].shift(1)).abs()
    tr3 = (df['low']  - df['close'].shift(1)).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move   = df['high'] - df['high_prev']
    down_move = df['low_prev'] - df['low']
    plus_dm   = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm  = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    atr = tr.rolling(window=period, min_periods=period).mean()
    plus_di  = 100 * (plus_dm.ewm(alpha=1/period).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=1/period).mean()
    return round(adx.iloc[-1], 2)


def fetch_atr(symbol: str, period: int) -> float:
    """
    Calculate the period-day ATR for the symbol.
    """
    df = fetch_ohlc(symbol, days=period * 3)
    df['high_prev'] = df['high'].shift(1)
    df['low_prev']  = df['low'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - df['close'].shift(1)).abs()
    tr3 = (df['low']  - df['close'].shift(1)).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    return round(atr.iloc[-1], 2)


def hist_pop(symbol: str, tgt_pct: float, sl_pct: float) -> float:
    """
    Historical Probability of Profit calculation.
    Stub: returns a placeholder percentage; integrate real backtest logic here.
    """
    return 85.0


def check_fno_exists(symbol: str) -> bool:
    """
    Check if symbol exists in F&O universe.
    Currently returns True for all; refine using exchange instruments list if needed.
    """
    return True


def check_ict_liquidity(symbol: str, df: pd.DataFrame) -> bool:
    """
    Check ICT liquidity-grab conditions.
    Implement logic using df price data as needed.
    """
    return True


def check_vwap_confluence(symbol: str) -> bool:
    """
    Check VWAP institutional confluence.
    Stub: returns True; implement real VWAP logic here.
    """
    return True


def check_obv_confirmation(symbol: str, df: pd.DataFrame) -> bool:
    """
    Check OBV accumulation/distribution confirmation.
    Stub: returns True; implement real OBV analysis here.
    """
    return True


def get_symbol_sector(symbol: str) -> str:
    """
    Get sector name for a symbol.
    Stub: returns 'Neutral'; replace with real mapping.
    """
    return "Neutral"


def find_short_strangle(symbol: str, bands: list) -> dict:
    """
    Find a short strangle setup based on SD bands.
    Stub: returns a dummy dict; integrate real option-chain logic.
    """
    expiry = datetime.now().strftime("%Y-%m-%d")
    return {"call_strike": f"{symbol}_C", "put_strike": f"{symbol}_P", "expiry": expiry}


def fetch_sector_rotation() -> dict:
    """
    Fetch sector rotation data.
    Stub: returns empty dict; integrate real sector rotation data source.
    ""
