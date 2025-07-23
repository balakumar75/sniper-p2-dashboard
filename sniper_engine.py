"""
sniper_engine.py  •  simplified “live” version

Flow
────
1. Build the F&O universe from instruments.py
2. Keep only symbols that have an instrument_token mapping
3. Rank by 14-period RSI (utils.fetch_rsi)
4. For the Top-N names, create trade dictionaries with all fields needed
   by the dashboard (date, entry, cmp, target, sl, pop, status, pnl, …)

You can later:
• Replace the stub F&O token map with the full NSE dump
• Upgrade PoP logic, option strikes, position sizing, etc.
"""

from typing import List, Dict, Tuple
from datetime import date
from instruments import FNO_SYMBOLS, SYMBOL_TO_TOKEN
from utils import fetch_rsi, gate, set_kite, _kite          # _kite is injected by sniper_run_all

# ── CONFIG ────────────────────────────────────────────────────────────────
TOP_N_MOMENTUM = 10          # keep the highest-RSI N symbols
DEFAULT_SL_PCT = 2.0         # stop-loss %
DEFAULT_TGT_PCT = 3.0        # target %
RSI_BUY_THRESHOLD = 55       # RSI above this → “Buy”, else “Hold”

# ── 0. helpers ────────────────────────────────────────────────────────────
def prefilter_candidates() -> List[str]:
    """Return symbols that exist in both FNO list and token map."""
    return [s for s in FNO_SYMBOLS if s in SYMBOL_TO_TOKEN]

def fetch_cmp(symbol: str) -> float | None:
    """
    Lightweight CMP via kite.ltp().  Returns None on error.
    `_kite` is set by sniper_run_all.py (utils.set_kite()).
    """
    try:
        gate()   # rate-limit
        ltp = _kite.ltp(f"NSE:{symbol}")
        return round(ltp[f"NSE:{symbol}"]["last_price"], 2)
    except Exception:
        return None

# ── 1. main API ───────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    """
    Produce list[dict] with the fields the dashboard expects.
    """
    universe: list[str] = prefilter_candidates()

    # Compute RSI for every symbol and skip failures (RSI == -1)
    rsi_pairs: list[Tuple[str, float]] = []
    for sym in universe:
        rsi_val = fetch_rsi(sym)
        if rsi_val != -1:
            rsi_pairs.append((sym, rsi_val))

    # Rank & keep top N
    ranked = sorted(rsi_pairs, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]

    trades: List[Dict] = []
    today_str = date.today().isoformat()

    for symbol, rsi_val in ranked:
        cmp_price = fetch_cmp(symbol)               # current market price
        if cmp_price is None:
            continue                                # skip if CMP unavailable

        trade_type = "Cash"                         # placeholder (“Fut” later)
        action     = "Buy" if rsi_val >= RSI_BUY_THRESHOLD else "Hold"

        trade = {
            "date":    today_str,
            "symbol":  symbol,
            "type":    trade_type,
            "entry":   cmp_price,
            "cmp":     cmp_price,                   # same at creation
            "target":  round(cmp_price * (1 + DEFAULT_TGT_PCT / 100), 2),
            "sl":      round(cmp_price * (1 - DEFAULT_SL_PCT / 100), 2),
            "pop":     "—",                         # plug real PoP later
            "status":  "Open",
            "pnl":     0.0,
            "action":  action,
            "rsi":     rsi_val,
        }
        trades.append(trade)

    return trades
