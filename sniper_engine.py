"""
sniper_engine.py
Core scanner that:
  1) Builds an initial universe   (prefilter_candidates)
  2) Ranks symbols by RSI         (utils.fetch_rsi)
  3) Returns a simple trade list  (list[dict])

You can later replace the stubbed parts (prefilter, trade dict, etc.)
with your full selection & position-sizing logic.
"""

from typing import List, Dict, Tuple
from utils import fetch_rsi

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
TOP_N_MOMENTUM = 10        # keep the highest-RSI N symbols
DEFAULT_SL_PCT = 2.0       # stop-loss percentage
DEFAULT_TGT_PCT = 3.0      # target percentage

# ---------------------------------------------------------------------------
# 0. QUICK UNIVERSE STUB  (replace with real filters later)
# ---------------------------------------------------------------------------
def prefilter_candidates() -> List[Tuple[str]]:
    """
    Return a list of tuples.  The first element MUST be the symbol string,
    because generate_sniper_trades() uses t[0] when calling fetch_rsi().

    Right now we simply load a hard-coded F&O universe so the engine runs.
    Replace this with your real filter pipeline (price, volume, sector, etc.).
    """
    # If you already maintain FNO_SYMBOLS elsewhere, import it here.
    FNO_SYMBOLS = [
        "RELIANCE", "HDFCBANK", "INFY", "TCS", "LTIM",
        "ICICIBANK", "SBIN", "TITAN", "ONGC", "CIPLA",
        # … add more or import from a data file …
    ]
    return [(sym,) for sym in FNO_SYMBOLS]

# ---------------------------------------------------------------------------
# 1.  MOMENTUM-BASED SNIPER LIST
# ---------------------------------------------------------------------------
def generate_sniper_trades() -> List[Dict]:
    """
    Build the final list of trade dictionaries.  Each dict must at least
    contain 'symbol', 'action', 'sl', 'target', so downstream code works.
    """
    # 1️⃣  initial screen
    validated = prefilter_candidates()

    # 2️⃣  drop symbols where RSI could not be computed (-1 sentinel)
    valid_with_rsi = [
        t for t in validated
        if fetch_rsi(t[0]) != -1
    ]

    # 3️⃣  rank by RSI
    ranked = sorted(
        valid_with_rsi,
        key=lambda x: fetch_rsi(x[0]),
        reverse=True
    )[:TOP_N_MOMENTUM]

    # 4️⃣  convert to simple trade dicts
    trades: List[Dict] = []
    for sym_tuple in ranked:
        symbol = sym_tuple[0]
        rsi_val = fetch_rsi(symbol)
        trade = {
            "symbol": symbol,
            "action": "Buy" if rsi_val >= 55 else "Hold",
            "rsi":    rsi_val,
            "sl_pct": DEFAULT_SL_PCT,
            "tgt_pct": DEFAULT_TGT_PCT,
        }
        trades.append(trade)

    return trades
