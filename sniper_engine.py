"""
sniper_engine.py
Cash Long/Short + 1 σ OTM SHORT Strangle

Filters
  • RSI ≥ 55
  • ADX ≥ 20
  • IV-Rank ≥ 33 %  (or IV fetch failed)
  • MACD bullish
  • Volume ≥ 1.5 × 20-day avg

Trigger
  • 50-bar Donchian channel breakout (close ≥ 50-day high for longs, ≤ 50-day low for shorts)
"""

import json, math, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, iv_rank,
)

# ── parameters ────────────────────────────────────────────────────────────
DONCHIAN_WINDOW = 50            # ← widened from 20 to 50
N_SIGMA         = 1.0
SIGMA_FALLBACKS = [1.25, 1.5]


# ── filter helpers ────────────────────────────────────────────────────────
def _validate(sym: str, cmp_: float) -> bool:
    if cmp_ is None:
        return False

    if fetch_rsi(sym) < RSI_MIN or fetch_adx(sym) < ADX_MIN:
        return False

    ivr = iv_rank(sym)          # 0.0 means IV fetch failed
    if ivr and ivr < 0.33:
        return False

    if not fetch_macd(sym):
        return False

    if fetch_volume(sym) <= 1.5:
        return False

    return True


def _breakout_dir(sym: str, cmp_: float) -> str | None:
    """Return 'up' or 'down' if price breaks 50-bar Donchian, else None."""
    high, low = donchian_high_low(sym, DONCHIAN_WINDOW)
    if high and cmp_ >= high:
        return "up"
    if low and cmp_ <= low:
        return "down"
    return None


# ── trade builders ────────────────────────────────────────────────────────
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


def _strangle(sym: str, cmp_: float, oc: dict, sigma: float, days: int):
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
        "tags": [f"{sigma:.2f}σ", "DC✅", "IVR✅", oc["expiry"]],
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


# ── engine loop ───────────────────────────────────────────────────────────
def generate_sniper_trades() -> list[dict]:
    trades: list[dict] = []

    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_):
            continue

        direction = _breakout_dir(sym, cmp_)
        if direction is None:
            continue

        # cash trade
        trades.append(_cash_trade(sym, cmp_, direction))

        # option strangle
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


def save_trades_to_json(trades: list[dict]) -> None:
    with open("trades.json", "w", encoding="utf-8") as fp:
        json.dump(trades, fp, indent=2)


if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
