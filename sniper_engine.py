"""
Main Sniper Engine
"""
from utils import fetch_rsi
from rate_limiter import gate
# other existing imports…

TOP_N_MOMENTUM = 10   # whatever you use

# ---------------------------------------------------------------------------
def generate_sniper_trades():
    """
    Core scanner – returns list[dict] describing trades
    """
    validated = prefilter_candidates()   # your existing preliminary list

    # Skip symbols where RSI could not be calculated (RSI == -1)
    valid_with_rsi = [
        t for t in validated
        if fetch_rsi(t[0]) != -1
    ]

    top_rsi = sorted(
        valid_with_rsi,
        key=lambda x: fetch_rsi(x[0]),
        reverse=True
    )[:TOP_N_MOMENTUM]

    # ... rest of your engine logic continues unchanged ...
    return build_trade_dicts(top_rsi)
