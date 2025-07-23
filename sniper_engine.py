"""
sniper_engine.py
Quick-start version that:

1. Loads the F&O universe from instruments.py
2. Keeps only symbols whose token exists in SYMBOL_TO_TOKEN
3. Ranks by RSI (utils.fetch_rsi) – skips failures automatically
4. Returns top N trade dicts
"""

from typing import List, Dict, Tuple
from instruments import FNO_SYMBOLS, SYMBOL_TO_TOKEN
from utils import fetch_rsi

TOP_N_MOMENTUM = 10        # number of trades to keep
DEFAULT_SL_PCT = 2.0
DEFAULT_TGT_PCT = 3.0


# ---------------------------------------------------------------------------
def prefilter_candidates() -> List[Tuple[str]]:
    """
    Basic pre-filter:
      • symbol in F&O universe
      • we have a token mapping for it
    Returns tuples (symbol,) because generate_sniper_trades() indexes [0].
    """
    return [
        (sym,)
        for sym in FNO_SYMBOLS
        if sym in SYMBOL_TO_TOKEN
    ]


# ---------------------------------------------------------------------------
def generate_sniper_trades() -> List[Dict]:
    """
    Generate a list[dict] with minimal fields so downstream code works.
    """
    universe = prefilter_candidates()

    # Skip symbols where RSI cannot be calculated (RSI == -1)
    symbols_with_rsi = [
        (t, fetch_rsi(t[0]))
        for t in universe
    ]
    symbols_with_rsi = [
        (sym_tuple, rsi)
        for sym_tuple, rsi in symbols_with_rsi
        if rsi != -1
    ]

    # Rank by RSI descending
    ranked = sorted(
        symbols_with_rsi,
        key=lambda x: x[1],            # sort key = rsi value
        reverse=True
    )[:TOP_N_MOMENTUM]

    # Build trade dicts
    trades: List[Dict] = []
    for (sym_tuple, rsi_val) in ranked:
        symbol = sym_tuple[0]
        trades.append(
            {
                "symbol":  symbol,
                "action":  "Buy" if rsi_val >= 55 else "Hold",
                "rsi":     rsi_val,
                "sl_pct":  DEFAULT_SL_PCT,
                "tgt_pct": DEFAULT_TGT_PCT,
            }
        )

    return trades
