"""
sniper_engine.py  •  Naked Short-Strangle Ideas (High PoP, Minimal Filters)
"""
from typing import List, Dict
from datetime import date, timedelta
import math

from instruments import FNO_SYMBOLS
import utils

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50         # ₹Cr (20-day avg)
STRANGLE_DTE     = 30        # days until expiry
ATR_WIDTH        = 1.0       # ±1 × ATR strike width
POPCUT           = 0.70      # require ≥70% combined PoP
TOP_N            = 10        # max ideas to return

# ── EXPIRY FINDER ───────────────────────────────────────────────────────────
def next_expiry(days_out=STRANGLE_DTE):
    today = date.today()
    e = date(today.year, today.month, 28)
    while e.weekday() != 3:  # back up to the most recent Thursday
        e -= timedelta(days=1)
    if (e - today).days < days_out:
        # roll to next month’s expiry
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        e = date(y, m, 28)
        while e.weekday() != 3:
            e -= timedelta(days=1)
    return e

# ── Black–Scholes Δ & norm_CDF ──────────────────────────────────────────────
def norm_cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2

def bs_delta(spot, strike, dte, call=True, vol=0.25, r=0.05):
    t = dte / 365
    d1 = (math.log(spot/strike) + (r + 0.5*vol*vol)*t) / (vol*math.sqrt(t))
    return (math.exp(-r*t) * norm_cdf(d1)) if call else (-math.exp(-r*t) * norm_cdf(-d1))

# ── ROUND helpers ───────────────────────────────────────────────────────────
def round_down(x, step): return int(x // step * step)
def round_up(x,   step): return int(math.ceil(x/step) * step)

# ── MAIN generator ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    ideas: List[Dict] = []
    today = date.today().isoformat()

    for sym in FNO_SYMBOLS:
        # 1) liquidity filter
        df = utils.fetch_ohlc(sym, 60)
        # fix ambiguous truth: check None or empty explicitly
        if df is None or df.empty:
            continue

        avg_turn = (df["close"] * df["volume"]).rolling(20).mean().iloc[-1] / 1e7
        if avg_turn < MIN_TURNOVER_CR:
            continue

        # 2) spot & ATR
        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df, 14).iloc[-1]
        width = ATR_WIDTH * atr14

        # 3) strikes
        put_strike  = round_down(spot - width, 50)
        call_strike = round_up(spot + width,  50)

        # 4) expiry & dte
        exp = next_expiry()
        dte = (exp - date.today()).days

        # 5) deltas & PoP
        delta_p = bs_delta(spot, put_strike,  dte, call=False)
        delta_c = bs_delta(spot, call_strike, dte, call=True)
        pop_p   = 1 - abs(delta_p)
        pop_c   = 1 - abs(delta_c)
        combo   = round(pop_p * pop_c, 2)

        # 6) keep only juicy combos
        if combo < POPCUT:
            continue

        ideas.append({
            "date":     today,
            "symbol":   sym,
            "strategy": "ShortStrangle",
            "entry":    0,      # premium fill later
            "cmp":      spot,
            "target":   0,
            "sl":       0,
            "pop":      combo,
            "action":   "Sell",
            "notes": {
                "expiry":      exp.isoformat(),
                "put_strike":  put_strike,
                "call_strike": call_strike,
                "delta_p":     round(delta_p, 2),
                "delta_c":     round(delta_c, 2),
            },
        })

    # return top-N by PoP
    return sorted(ideas, key=lambda t: t["pop"], reverse=True)[:TOP_N]
