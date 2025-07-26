"""
instruments.py

Defines:
- FNO_SYMBOLS
- SYMBOL_TO_TOKEN
- FUTURE_TOKENS (futures by expiry)
- OPTION_TOKENS (options by expiry, type, strike)
"""

# ── Your F&O universe ───────────────────────────────────────────────────────
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "SBIN",      "LTIM",     "TITAN",     "ONGC", "CIPLA",
]

# ── Spot mapping: symbol → instrument_token ─────────────────────────────────
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

# ── Futures by expiry (YYYY-MM-DD) ─────────────────────────────────────────
# Replace the zeros with the real instrument_tokens for each contract
FUTURE_TOKENS = {
    sym: {
        "2025-07-31": 0,
        "2025-08-28": 0,
    }
    for sym in FNO_SYMBOLS
}

# ── Options by expiry → type → strike → token ──────────────────────────────
# Replace the zeros with the real instrument_tokens for each option
OPTION_TOKENS = {
    sym: {
        "2025-07-31": {
            "PE": {800: 0, 780: 0},
            "CE": {820: 0, 840: 0},
        },
        # add other expiries as needed
    }
    for sym in FNO_SYMBOLS
}
