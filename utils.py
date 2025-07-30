# utils.py

import pandas as pd
import numpy as np

# Global kite client placeholder
_kite = None

def set_kite(kite_client):
    """
    Set the global Kite Connect client for use in API-based utils.
    """
    global _kite
    _kite = kite_client


def fetch_ohlc(symbol: str, days: int) -> pd.DataFrame:
    """
    Fetch OHLC data for the symbol over the past `days` days.
    Stub: returns synthetic closing price data for testing.
    """
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    closes = np.linspace(100, 100 + days, days)
    return pd.DataFrame({"close": closes}, index=dates)


def fetch_rsi(symbol: str, period: int) -> float:
    """
    Calculate RSI for the symbol.
    Stub: returns a constant value above the RSI_MIN threshold.
    """
    return 60.0


def fetch_adx(symbol: str, period: int) -> float:
    """
    Calculate ADX for the symbol.
    Stub: returns a constant value above the ADX_MIN threshold.
    """
    return 25.0


def fetch_atr(symbol: str, period: int) -> float:
    """
    Calculate ATR for the symbol.
    Stub: returns a constant ATR value.
    """
    return 1.0


def hist_pop(symbol: str, tgt_pct: float, sl_pct: float) -> float:
    """
    Historical Probability of Profit calculation.
    Stub: returns a constant PoP percentage.
    """
    return 85.0


def check_fno_exists(symbol: str) -> bool:
    """
    Check if symbol exists in F&O universe.
    Stub: always returns True.
    """
    return True


def check_ict_liquidity(symbol: str, df: pd.DataFrame) -> bool:
    """
    Check ICT liquidity-grab conditions.
    Stub: always returns True.
    """
    return True


def check_vwap_confluence(symbol: str) -> bool:
    """
    Check VWAP institutional confluence.
    Stub: always returns True.
    """
    return True


def check_obv_confirmation(symbol: str, df: pd.DataFrame) -> bool:
    """
    Check OBV accumulation/distribution confirmation.
    Stub: always returns True.
    """
    return True


def get_symbol_sector(symbol: str) -> str:
    """
    Get sector name for a symbol.
    Stub: returns 'Neutral'.
    """
    return "Neutral"


def find_short_strangle(symbol: str, bands: list) -> dict:
    """
    Find a short strangle setup based on SD bands.
    Stub: returns a dummy non-empty dict for testing.
    """
    return {
        "call_strike": f"{symbol}_C",  # placeholder
        "put_strike":  f"{symbol}_P",  # placeholder
        "expiry":      pd.Timestamp.today().strftime("%Y-%m-%d")
    }


def fetch_sector_rotation() -> dict:
    """
    Fetch sector rotation data.
    Stub: returns an empty dict so all sectors default to Neutral.
    """
    return {}
