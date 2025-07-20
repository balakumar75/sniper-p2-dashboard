"""
sniper_engine.py  –  Cash + Volatility-based OTM Short Strangle
"""

import json, math, statistics, pathlib
from datetime import datetime
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN, VOL_MULTIPLIER
from utils  import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain, fetch_ohlc
)

# ── Parameters (tweak here or via sniper_params.json) ──────────────────────
N_SIGMA   = 1.0     # 1σ OTM; tuner can raise to 1.25 or 1.5
SIGMA_FALLBACKS = [1.25, 1.5]

# ── Helpers ───────────────────────────────────────────────────────────────
def _hist_vol(symbol):
    """Return annualised stdev of daily log-returns (σ_year)."""
    df = fetch_ohlc(symbol, 60)      # 60 trading days
    if df is None or df.empty: return None
    import math, statistics
    log_rets = [math.log(c2/c1) for c1,c2 in zip(df.close[:-1], df.close[1:])]
    sigma_daily = statistics.stdev(log_rets) if len(log_rets) > 3 else None
    return None if sigma_daily is None else sigma_daily * math.sqrt(252)

def _validate(symbol, cmp_):
    if cmp_ is None:                           return False
    if fetch_rsi(symbol)   < RSI_MIN:          return False
    if fetch_adx(symbol)   < ADX_MIN:          return False
    if not fetch_macd(symbol):                 return False
    if not fetch_volume(symbol):               return False
    return True

def _cash_trade(sym, cmp_):
    return {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym, "type": "Cash",
        "entry": cmp_, "cmp": cmp_,
        "target": round(cmp_ * 1.02, 2),
        "sl":     round(cmp_ * 0.975, 2),
        "pop_pct": DEFAULT_POP, "action": "Buy",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅","MACD✅"],
        "status": "Open", "exit_date": "-", "pnl": 0.0
    }

def _pick_by_sigma(cmp_, oc, sigma, days_to_exp):
    """Return (call_strike, put_strike) for given σ multiple or None."""
    band = sigma * math.sqrt(days_to_exp/365)
    ce = min((s for s in oc["CE"] if s >= cmp_*(1+band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_*(1-band)), default=None)
    return (ce, pe) if ce and pe else None

def _short_strangle(sym, cmp_, oc, sigma, days_to_exp):
    strikes = _pick_by_sigma(cmp_, oc, sigma, days_to_exp)
    if not strikes:
        return None
    ce_strike, pe_strike = strikes
    ce_ltp = oc["ltp_map"][ce_strike];  pe_ltp = oc["ltp_map"][pe_strike]
    credit = round((ce_ltp + pe_ltp) / 2, 2)
    return {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,  "type": "Option Strangle",
        "entry": credit, "cmp": credit,
        "target": round(credit * 0.70, 2),
        "sl":     round(credit * 1.60, 2),
        "pop_pct": f"{int(sigma*100)}%",      # rough label
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sigma:.2f}σ", oc["expiry"]],
        "options": {
            "expiry": oc["expiry"],
            "call":   ce_strike, "put": pe_strike,
            "call_ltp": ce_ltp,  "put_ltp":  pe_ltp
        },
        "status": "Open", "exit_date": "-", "pnl": 0.0
    }

# ── Engine ────────────────────────────────────────────────────────────────
def generate_sniper_trades():
    trades = []
    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_): continue

        t
