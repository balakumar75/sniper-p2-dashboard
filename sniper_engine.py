"""
sniper_engine.py
Tier-1  : 20-bar breakout  → Cash + 1 σ strangle
Tier-2  : highest-RSI F&O names → 1.25 σ strangle  (if no Tier-1)
Tier-3  : highest-RSI (any) → Cash trade             (if still empty)
"""

import json, math, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, iv_rank,
)

# ── parameters ───────────────────────────────────────────────────────────
DONCHIAN_WINDOW   = 20
VOL_THRESHOLD     = 1.0
N_SIGMA_BREAKOUT  = 1.0
N_SIGMA_MOMENTUM  = 1.25           # for option fallback
TOP_N_MOMENTUM    = 5              # how many cash fallbacks

# ── diagnostics ──────────────────────────────────────────────────────────
fail = {"RSI": 0, "ADX": 0, "MACD": 0, "VOL": 0}

# ── filter helpers ───────────────────────────────────────────────────────
def _validate(sym, cmp_):
    if cmp_ is None:
        return False
    if fetch_rsi(sym) < RSI_MIN:
        fail["RSI"] += 1; return False
    if fetch_adx(sym) < ADX_MIN:
        fail["ADX"] += 1; return False
    ivr = iv_rank(sym)
    if ivr and ivr < 0.33:
        return False
    if not fetch_macd(sym):
        fail["MACD"] += 1; return False
    if fetch_volume(sym) <= VOL_THRESHOLD:
        fail["VOL"] += 1; return False
    return True

def _breakout_dir(sym, cmp_):
    hi, lo = donchian_high_low(sym, DONCHIAN_WINDOW)
    if hi and cmp_ >= hi: return "up"
    if lo and cmp_ <= lo: return "down"
    return None

# ── trade builders ───────────────────────────────────────────────────────
def _cash(sym, cmp_, direction, tag):
    long = direction == "up"
    tgt  = round(cmp_ * (1.02 if long else 0.98), 2)
    sl   = round(cmp_ * (0.975 if long else 1.025), 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Cash",
        "entry": cmp_,
        "cmp":   cmp_,
        "target": tgt,
        "sl": sl,
        "pop_pct": DEFAULT_POP,
        "action": "Buy" if long else "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅", tag],
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0,
    }

def _strangle(sym, cmp_, oc, sigma, extra_tag=""):
    band = sigma * math.sqrt(oc["days_to_exp"] / 365)
    ce = min((s for s in oc["CE"] if s >= cmp_ * (1 + band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_ * (1 - band)), default=None)
    if not (ce and pe):
        return None
    credit = round((oc["ltp_map"][ce] + oc["ltp_map"][pe]) / 2, 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Option Strangle",
        "entry": credit,
        "cmp": credit,
        "target": round(credit * 0.70, 2),
        "sl": round(credit * 1.60, 2),
        "pop_pct": f"{int(sigma*100)}%",
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sigma:.2f}σ", oc["expiry"]] + ([extra_tag] if extra_tag else []),
        "options": {"expiry": oc["expiry"], "call": ce, "put": pe,
                    "call_ltp": oc["ltp_map"][ce], "put_ltp": oc["ltp_map"][pe]},
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0,
    }

# ── main engine ──────────────────────────────────────────────────────────
def generate_sniper_trades():
    trades, validated, breakout = [], [], 0

    # pass 1: breakout scan
    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_):
            continue
        validated.append((sym, cmp_))
        dir_ = _breakout_dir(sym, cmp_)
        if dir_ is None:
            continue
        breakout += 1
        trades.append(_cash(sym, cmp_, dir_, "DC✅"))

        oc = fetch_option_chain(sym)
        if oc:
            tr = _strangle(sym, cmp_, oc, N_SIGMA_BREAKOUT, "DC✅")
            if tr:
                trades.append(tr)

    # pass 2: option-strangle momentum fallback
    if not trades and validated:
        top_rsi = sorted(validated, key=lambda x: fetch_rsi(x[0]), reverse=True)[:TOP_N_MOMENTUM]
        for sym, cmp_ in top_rsi:
            oc = fetch_option_chain(sym)
            if not oc:
                continue
            tr = _strangle(sym, cmp_, oc, N_SIGMA_MOMENTUM, "MOM✅")
            if tr:
                trades.append(tr)

    # pass 3: cash momentum fallback
    if not trades and validated:
        top_rsi = sorted(validated, key=lambda x: fetch_rsi(x[0]), reverse=True)[:TOP_N_MOMENTUM]
        for sym, cmp_ in top_rsi:
            trades.append(_cash(sym, cmp_, "up", "MOM✅"))

    print("fail breakdown:", fail)
    print(f"validated: {len(validated)}, breakout: {breakout}, trades: {len(trades)}")
    return trades

def save_trades_to_json(t):
    with open("trades.json", "w", encoding="utf-8") as fp:
        json.dump(t, fp, indent=2)

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
