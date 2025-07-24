"""
instruments.py

Defines the list of F&O symbols to scan (FNO_SYMBOLS) and a mapping
from symbol → instrument_token (SYMBOL_TO_TOKEN) for KiteConnect.

Replace any placeholder token values (<TOKEN>) with the correct number
from your Kite instruments dump or by calling kite.ltp() interactively.
"""

# ── Your F&O universe ───────────────────────────────────────────────────────
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "SBIN",      "LTIM",     "TITAN",     "ONGC", "CIPLA",
]

# ── Mapping symbol → instrument_token ──────────────────────────────────────
SYMBOL_TO_TOKEN = {
    "RELIANCE":  738561,
    "HDFCBANK":  341249,
    "ICICIBANK": 1270529,
    "INFY":      408065,
    "TCS":       2953217,
    "SBIN":      779521,
    "LTIM":      2631937,   # ← replace <TOKEN> with actual if this is wrong
    "TITAN":     10005857,
    "ONGC":      5409281,
    "CIPLA":     350067,
}
