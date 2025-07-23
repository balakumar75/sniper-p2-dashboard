"""
sniper_engine.py – live version with PoP column
"""
from typing import List, Dict, Tuple
from datetime import date
from instruments import FNO_SYMBOLS, SYMBOL_TO_TOKEN
from utils import fetch_rsi, hist_pop, gate, _kite

# ── CONFIG ────────────────────────────────────────────────────────────────
TOP_N_MOMENTUM   = 10
DEFAULT_SL_PCT   = 2.0
DEFAULT_TGT_PCT  = 3.0
RSI_BUY_THRESHOLD = 55

# ── helpers ───────────────────────────────────────────────────────────────
def prefilter_candidates() -> List[str]:
    return [s for s in FNO_SYMBOLS if s in SYMBOL_TO_TOKEN]

def fetch_cmp(symbol: str) -> float | None:
    try:
        gate()
        ltp = _kite.ltp(f"NSE:{symbol}")
        return round(ltp[f"NSE:{symbol}"]["last_price"], 2)
    except Exception:
        return None

# ── main generator ────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    universe = prefilter_candidates()

    rsi_pairs: List[Tuple[str, float]] = []
    for sym in universe:
        rsi_val = fetch_rsi(sym)
        if rsi_val != -1:
            rsi_pairs.append((sym, rsi_val))

    ranked = sorted(rsi_pairs, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]

    trades: List[Dict] = []
    today_str = date.today().isoformat()

    for symbol, rsi_val in ranked:
        cmp_price = fetch_cmp(symbol)
        if cmp_price is None:
            continue

        pop_val = hist_pop(symbol, DEFAULT_TGT_PCT, DEFAULT_SL_PCT)
        trade = {
            "date":    today_str,
            "symbol":  symbol,
            "type":    "Cash",
            "entry":   cmp_price,
            "cmp":     cmp_price,
            "target":  round(cmp_price * (1 + DEFAULT_TGT_PCT / 100), 2),
            "sl":      round(cmp_price * (1 - DEFAULT_SL_PCT / 100), 2),
            "pop":     pop_val if pop_val is not None else "—",
            "status":  "Open",
            "pnl":     0.0,
            "action":  "Buy" if rsi_val >= RSI_BUY_THRESHOLD else "Hold",
            "rsi":     rsi_val,
        }
        trades.append(trade)

    return trades
