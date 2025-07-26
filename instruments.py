"""
instruments.py

Defines your F&O universe and instrument tokens. Fill in the real token numbers
from KiteConnect for each expiry/strike you plan to trade.
"""
# Your F&O symbols
from config import FNO_SYMBOLS

# Spot mapping: symbol → instrument_token
SYMBOL_TO_TOKEN = {
    # e.g.
    "RELIANCE":  738561,
    "TCS":       2953217,
    "HDFCBANK":  341249,
    "INFY":      408065,
    "ICICIBANK": 1270529,
    # … add all FNO_SYMBOLS …
}

# Futures tokens by expiry (ISO date string → token)
FUTURE_TOKENS = {
    sym: {
        "2025-07-31": 0,   # ← replace 0 with the real token
        "2025-08-28": 0,
    }
    for sym in FNO_SYMBOLS
}

# Option tokens by expiry → type → strike → token
OPTION_TOKENS = {
    sym: {
        "2025-07-31": {
            "PE": {
                # 800: 12345678,
            },
            "CE": {
                # 840: 12345679,
            }
        }
    }
    for sym in FNO_SYMBOLS
}
