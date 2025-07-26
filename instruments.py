"""
instruments.py

F&O universe & instrument_token mappings.  Fill in the <REPLACE_WITH_TOKEN>
entries by querying kite.instruments("NFO") in a REPL.
"""
from config import FNO_SYMBOLS

# Spot mapping: symbol → instrument_token
SYMBOL_TO_TOKEN = {
    # Example:
    # "RELIANCE":  738561,
    # "TCS":       2953217,
    # ... fill for all FNO_SYMBOLS ...
}

# Futures tokens by expiry
# Replace <REPLACE_WITH_TOKEN> with the real token IDs
FUTURE_TOKENS = {
    sym: {
        "2025-07-31": <REPLACE_WITH_TOKEN>,   # e.g. 10526722
        "2025-08-28": <REPLACE_WITH_TOKEN>,
    }
    for sym in FNO_SYMBOLS
}

# Option tokens by expiry → type → strike → token
# Replace <REPLACE_WITH_TOKEN> in each map.
OPTION_TOKENS = {
    sym: {
        "2025-07-31": {
            "PE": {
                # 1400: <REPLACE_WITH_TOKEN>,
                # 1450: <REPLACE_WITH_TOKEN>,
            },
            "CE": {
                # 1500: <REPLACE_WITH_TOKEN>,
                # 1550: <REPLACE_WITH_TOKEN>,
            }
        }
    }
    for sym in FNO_SYMBOLS
}
