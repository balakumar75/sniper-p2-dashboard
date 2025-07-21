"""
sniper_engine.py – Cash + Vol-based 1 σ OTM SHORT Strangle
Adds 20-bar Donchian breakout **AND** TTM-squeeze filter.
"""

import json, math, statistics
from datetime import datetime
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils  import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, in_squeeze_breakout
)

# ── Parameters ───────────────────────────────────────────────────────────
N_SIGMA = 1.0
SIGMA_FALLBACKS = [1.25, 1.5]
DONCHIAN_WINDOW = 20

# ── Validation ───────────────────────────────────────────────────────────
def _validate(symbol, cmp_):
    if cmp_ is None:                      return False
    if fetch_rsi(symbol) < RSI_MIN:       return False
    if fetch_adx(symbol) < ADX_MIN:       return False
    if not fetch_macd(symbol):            return False
    if not fetch_volume(symbol):          return False
    # Donchian breakout
    high, _ = donchian_high_low(symbol, DONCHIAN_WINDOW)
    if high is None or cmp_ < high:       return False
    # Squeeze breakout
    if not in_squeeze_breakout(symbol):   return False
    return True

# ── Trade builders (cash & strangle) ─────────────────────────────────────
def _cash_trade(sym, cmp_):
    return {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym, "type": "Cash",
        "entry": cmp_, "cmp": cmp_,
        "target": round(cmp_ * 1.02, 2),
        "sl":     round(cmp_ * 0.975, 2),
        "pop_pct": DEFAULT_POP,
        "action": "Buy",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅","MACD✅","DC✅","SQ✅"],
        "status":"Open","exit_date":"-","pnl":0.0
    }

def _pick_by_sigma(cmp_, oc, sigma, days):
    band = sigma * math.sqrt(days/365)
    ce = min((s for s in oc["CE"] if s >= cmp_*(1+band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_*(1-band)), default=None)
    return (ce, pe) if ce and pe else None

def _short_strangle(sym, cmp_, oc, sigma, days):
    strikes = _pick_by_sigma(cmp_, oc, sigma, days)
    if not strikes: return None
    ce_strike, pe_strike = strikes
    credit = round((oc["ltp_map"][ce_strike] + oc["ltp_map"][pe_strike]) / 2, 2)
    return {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym, "type": "Option Strangle",
        "entry": credit, "cmp": credit,
        "target": round(credit*0.70, 2),
        "sl":     round(credit*1.60, 2),
        "pop_pct": f"{int(sigma*100)}%",
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sigma:.2f}σ","DC✅","SQ✅", oc["expiry"]],
        "options": {
            "expiry": oc["expiry"],
            "call": ce_strike, "put": pe_strike,
            "call_ltp": oc["ltp_map"][ce_strike],
            "put_ltp":  oc["ltp_map"][pe_strike]
        },
        "status":"Open","exit_date":"-","pnl":0.0
    }

# ── Engine ───────────────────────────────────────────────────────────────
def generate_sniper_trades():
    trades=[]
    for sym in FNO_SYMBOLS:
        cmp_=fetch_cmp(sym)
        if not _validate(sym, cmp_): continue
        trades.append(_cash_trade(sym, cmp_))
        oc = fetch_option_chain(sym)
        if not oc: continue
        days = oc.get("days_to_exp", 7)
        str_tr = _short_strangle(sym, cmp_, oc, N_SIGMA, days)
        if not str_tr:
            for sig in SIGMA_FALLBACKS:
                str_tr = _short_strangle(sym, cmp_, oc, sig, days)
                if str_tr: break
        if str_tr: trades.append(str_tr)
    print("✅ trades:", len(trades))
    return trades

def save_trades_to_json(tr):
    with open("trades.json","w",encoding="utf-8") as f: json.dump(tr,f,indent=2)

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
