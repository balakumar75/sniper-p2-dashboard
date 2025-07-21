"""
sniper_engine.py
Cash  (Long & Short) + Vol-based 1σ OTM SHORT Strangle
Filters: RSI · ADX · MACD · Volume · 20-bar Donchian breakout · 5-bar squeeze breakout
"""

import json, math, statistics, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils  import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, in_squeeze_breakout
)

N_SIGMA = 1.0
SIGMA_FALLBACKS = [1.25, 1.5]
DONCHIAN_WINDOW = 20

# ── Helpers ───────────────────────────────────────────────────────────────
def _validate(symbol, cmp_):
    if cmp_ is None: return False
    if fetch_rsi(symbol) < RSI_MIN:  return False
    if fetch_adx(symbol) < ADX_MIN:  return False
    if not fetch_macd(symbol):       return False
    if not fetch_volume(symbol):     return False
    return True

def _breakout_direction(symbol, cmp_):
    """Return 'up', 'down', or None based on Donchian + squeeze breakout."""
    high, low = donchian_high_low(symbol, DONCHIAN_WINDOW)
    if high is None: return None
    if cmp_ >= high and in_squeeze_breakout(symbol): return 'up'
    if cmp_ <= low  and in_squeeze_breakout(symbol, squeeze_bars=5): return 'down'
    return None

def _cash_trade(sym, cmp_, direction):
    long = direction == 'up'
    entry = cmp_
    target = round(entry * (1.02 if long else 0.98), 2)
    sl     = round(entry * (0.975 if long else 1.025), 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Cash",
        "entry": entry,
        "cmp": cmp_,
        "target": target,
        "sl": sl,
        "pop_pct": DEFAULT_POP,
        "action": "Buy" if long else "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅","MACD✅","DC✅","SQ✅"],
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0
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
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Option Strangle",
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
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0
    }

# ── Engine ───────────────────────────────────────────────────────────────
def generate_sniper_trades():
    trades = []
    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_): continue

        direction = _breakout_direction(sym, cmp_)
        if direction is None: continue          # skip symbols without breakout
        trades.append(_cash_trade(sym, cmp_, direction))

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
