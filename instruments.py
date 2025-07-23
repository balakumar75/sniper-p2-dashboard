"""
instruments.py
Minimal, hard-coded mapping so Sniper Engine can fetch OHLC without
needing the full NSE instruments dump.  Update or expand whenever you like.

token values are the “instrument_token” numbers from Zerodha’s
instruments.csv for the CURRENT expiry series of each stock future.
"""

# F&O universe you want to scan every day
FNO_SYMBOLS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
    "SBIN", "LTIM", "TITAN", "ONGC", "CIPLA",
    "KOTAKBANK", "MARUTI", "SUNPHARMA", "AXISBANK", "ITC",
]

# Minimal token map (5 examples filled in; add the rest later).
# Get tokens from Zerodha instruments dump or kite.ltp() output.
SYMBOL_TO_TOKEN = {
    "RELIANCE": 738561,
    "HDFCBANK": 341249,
    "ICICIBANK": 1270529,
    "INFY": 408065,
    "TCS": 2953217,
    # "SBIN": 779521,
    # "LTIM": <token>,
    # … fill others as you need …
}
