"""
instruments.py

Defines the list of F&O symbols to scan (FNO_SYMBOLS),
a mapping from symbol → instrument_token (SYMBOL_TO_TOKEN),
and future contract tokens by expiry (FUTURE_TOKENS) for KiteConnect.

Replace any placeholder token values (<TOKEN>) with the correct numbers
from your Kite instruments dump or by calling kite.ltp() interactively.
"""

# ── Your F&O universe ───────────────────────────────────────────────────────
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "SBIN",      "LTIM",     "TITAN",     "ONGC", "CIPLA",
]

# ── Mapping symbol → spot instrument_token ─────────────────────────────────
SYMBOL_TO_TOKEN = {
    "RELIANCE":  738561,
    "HDFCBANK":  341249,
    "ICICIBANK": 1270529,
    "INFY":      408065,
    "TCS":       2953217,
    "SBIN":      779521,
    "LTIM":      2631937,
    "TITAN":     10005857,
    "ONGC":      5409281,
    "CIPLA":     350067,
}

# ── Future contract tokens by expiry date (YYYY-MM-DD) ───────────────────────
# Fill in each expiry with the correct instrument_token for that futures contract.
FUTURE_TOKENS = {
    "RELIANCE": {
        "2025-07-31": 1234567,   # ← replace with actual token for Reliance July expiry
        "2025-08-28": 2345678,   # ← August expiry
        # add further expiries as needed
    },
    "HDFCBANK": {
        "2025-07-31": 2234567,
        "2025-08-28": 3345678,
    },
    "ICICIBANK": {
        "2025-07-31": 3234567,
        "2025-08-28": 4345678,
    },
    "INFY": {
        "2025-07-31": 4234567,
        "2025-08-28": 5345678,
    },
    "TCS": {
        "2025-07-31": 5234567,
        "2025-08-28": 6345678,
    },
    "SBIN": {
        "2025-07-31": 6234567,
        "2025-08-28": 7345678,
    },
    "LTIM": {
        "2025-07-31": 7234567,
        "2025-08-28": 8345678,
    },
    "TITAN": {
        "2025-07-31": 8234567,
        "2025-08-28": 9345678,
    },
    "ONGC": {
        "2025-07-31": 9234567,
        "2025-08-28": 10345678,
    },
    "CIPLA": {
        "2025-07-31": 10234567,
        "2025-08-28": 11345678,
    },
}
