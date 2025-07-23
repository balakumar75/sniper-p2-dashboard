"""
sniper_engine.py
Tier-1: 20-bar Donchian breakout  + Cash + 1 σ strangle
Tier-2 fallback (only if no breakouts):
        highest-RSI names that pass core filters, 1.25 σ strangle
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
N_SIGMA_PRIMARY   = 1.0
N_SIGMA_FALLBACKS = [1.25, 1.5]          # for breakout leg
N_SIGMA_MOMENTUM  = 1.25                 # for fallback leg

VOL_THRESHOLD = 1.0                      # ≥ 1.0 × 20-day avg

# ── diagnostics ──────────────────────────────────────────────────────────
fail_counts = {"RSI": 0, "ADX": 0, "MACD": 0, "VOL": 0}

# ── filter helpers ───────────────────────────────────────────────────────
def _validate(sym: str, cmp_: float) -> bool:
    if cmp_ is None:
        return False
    if fetch_rsi(sym) < RSI_MIN:
        fail_counts["RSI"] += 1
        return False
    if fetch_adx(sym) < ADX_MIN:
        fail_counts["ADX"] += 1
        return False
    ivr = iv_rank(sym)               # 0 ⇒ IV fetch failed → allow
    if ivr and ivr < 0.33:
        return False
    if not fetch_macd(sym):
        fail_counts["MACD"] += 1
        return False
    if fetch_volume(sym) <= VOL_THRESHOLD:
        fail_counts["VOL"] += 1
        return False
    return True


def _breakout_dir(sym: str, cmp_: float) -> str | None:
    hi, lo = donchian_high_low(sym, DONCHIAN_WINDOW)
    if hi and cmp_ >= hi:
        return "up"
    if lo and cmp_ <= lo:
        return "down"
    return None

# ── trade builders ───────────────────────────────────────────────────────
def _cash_trade(sym: str, cmp_: float, direction: str) -> dict:
    long = direction == "up"
    target = round(cmp_ * (1.02 if long else 0.98), 2)
    sl     = round(cmp_ * (0.975 if long else 1.025), 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Cash",
        "entry": cmp_,
        "cmp": cmp_,
        "target": target,
        "sl": sl,
        "pop_pct": DEFAULT_POP,
        "action": "Buy" if long else "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅", "MACD✅", "DC✅", "IVR✅"],
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0,
    }

def _pick_strikes(cmp_: float, oc: dict, sigma: float, days: int):
    band = sigma * math.sqrt(days / 365)
    ce = min((s for s in oc["CE"] if s >= cmp_ * (1 + band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_ * (1 - band)), default=None)
    return (ce, pe) if ce and pe else None

def _strangle_trade(sym, cmp_, oc, sigma, days, tag_extra=""):
    strikes = _pick_strikes(cmp_, oc, sigma, days)
    if not strikes:
        return None
    ce, pe = strikes
    credit = round((oc["ltp_map"][ce] + oc["ltp_map"][pe]) / 2, 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Option Strangle",
        "entry": credit,
        "cmp": credit,
        "target": round(credit * 0.70, 2),
        "sl": round(credit * 1.60, 2),
        "pop_pct": f"{int(sigma * 100)}%",
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sigma:.2f}σ", "IVR✅", oc["expiry"]] + ( [tag_extra] if tag_extra else [] ),
        "options": {
            "expiry": oc["expiry"],
            "call": ce,
            "put": pe,
            "call_ltp": oc["ltp_map"][ce],
            "put_ltp": oc["ltp_map"][pe],
        },
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0,
    }

# ── main engine ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> list[dict]:
    trades = []
    validated, breakout = 0, 0
    validated_syms = []          # store for fallback

    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_):
            continue
        validated += 1
        validated_syms.append((sym, cmp_))

        direction = _breakout_dir(sym, cmp_)
        if direction is None:
            continue
        breakout += 1

        # cash leg
        trades.append(_cash_trade(sym, cmp_, direction))

        # 1 σ strangle leg
        oc = fetch_option_chain(sym)
        if oc:
            days = oc.get("days_to_exp", 7)
            tr = _strangle_trade(sym, cmp_, oc, N_SIGMA_PRIMARY, days)
            if not tr:
                for sig in N_SIGMA_FALLBACKS:
                    tr = _strangle_trade(sym, cmp_, oc, sig, days)
                    if tr:
                        break
            if tr:
                trades.append(tr)

    # ── Fallback: highest-RSI momentum strangle if no breakout trades
    if not trades:
        top = sorted(validated_syms, key=lambda x: fetch_rsi(x[0]), reverse=True)[:5]
        for sym, cmp_ in top:
            oc = fetch_option_chain(sym)
            if not oc:
                continue
            days = oc.get("days_to_exp", 7)
            trade = _strangle_trade(sym, cmp_, oc, N_SIGMA_MOMENTUM, days, tag_extra="MOM✅")
            if trade:
                trades.append(trade)

    print("fail breakdown:", fail_counts)
    print(f"stats: {{'validated': {validated}, 'breakout': {breakout}}}")
    print(f"✅ trades: {len(trades)}")
    return trades

def save_trades_to_json(trades):
    with open("trades.json", "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2)

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
