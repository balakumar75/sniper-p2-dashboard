""" sniper_engine.py – Cash + Short-Strangle """

import json, math, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, in_squeeze_breakout, iv_rank,
)

N_SIGMA = 1.0
SIGMA_FALLBACKS = [1.25, 1.5]

# ── filters ────────────────────────────────────────────────────────────
def _validate(sym: str, cmp_: float) -> bool:
    if cmp_ is None:
        return False
    if fetch_rsi(sym) < RSI_MIN or fetch_adx(sym) < ADX_MIN:
        return False
    ivr = iv_rank(sym)          # 0.0 if IV fetch failed
    if ivr and ivr < 0.33:
        return False
    if not fetch_macd(sym):
        return False
    if fetch_volume(sym) <= 1.5:
        return False
    return True

def _breakout_dir(sym: str, cmp_: float) -> str | None:
    hi, lo = donchian_high_low(sym, 20)
    if hi and cmp_ >= hi and in_squeeze_breakout(sym, direction="up"):
        return "up"
    if lo and cmp_ <= lo and in_squeeze_breakout(sym, direction="down"):
        return "down"
    return None

# ── builders ────────────────────────────────────────────────────────────
def _cash_trade(sym: str, cmp_: float, direction: str) -> dict:
    long = direction == "up"
    tgt  = round(cmp_ * (1.02 if long else 0.98), 2)
    sl   = round(cmp_ * (0.975 if long else 1.025), 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Cash",
        "entry": cmp_,
        "cmp": cmp_,
        "target": tgt,
        "sl": sl,
        "pop_pct": DEFAULT_POP,
        "action": "Buy" if long else "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅", "MACD✅", "DC✅", "SQ✅", "IVR✅"],
        "status": "Open",
        "exit_date": "-",
        "holding_days": 0,
        "pnl": 0.0,
    }

def _pick(cmp_: float, oc: dict, sig: float, days: int):
    band = sig * math.sqrt(days / 365)
    ce = min((s for s in oc["CE"] if s >= cmp_ * (1 + band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_ * (1 - band)), default=None)
    return (ce, pe) if ce and pe else None

def _strangle(sym: str, cmp_: float, oc: dict, sig: float, days: int):
    strike_pair = _pick(cmp_, oc, sig, days)
    if not strike_pair:
        return None
    ce, pe = strike_pair
    credit = round((oc["ltp_map"][ce] + oc["ltp_map"][pe]) / 2, 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym,
        "type": "Option Strangle",
        "entry": credit,
        "cmp": credit,
        "target": round(credit * 0.70, 2),
        "sl": round(credit * 1.60, 2),
        "pop_pct": f"{int(sig * 100)}%",
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sig:.2f}σ", "DC✅", "SQ✅", "IVR✅", oc["expiry"]],
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

# ── main engine ─────────────────────────────────────────────────────────
def generate_sniper_trades() -> list[dict]:
    trades: list[dict] = []

    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_):
            continue

        direction = _breakout_dir(sym, cmp_)
        if direction is None:
            continue

        # cash leg
        trades.append(_cash_trade(sym, cmp_, direction))

        # strangle leg
        oc = fetch_option_chain(sym)
        if oc:
            days = oc.get("days_to_exp", 7)
            tr = _strangle(sym, cmp_, oc, N_SIGMA, days)
            if not tr:
                for sig in SIGMA_FALLBACKS:
                    tr = _strangle(sym, cmp_, oc, sig, days)
                    if tr:
                        break
            if tr:
                trades.append(tr)

    print(f"✅ trades: {len(trades)}")
    return trades

def save_trades_to_json(trades):
    with open("trades.json", "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2)

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
