"""
sniper_engine.py  •  Strangles + RSI‐fallback engine
"""
from typing import List, Dict
from datetime import date, timedelta
import math

from instruments import FNO_SYMBOLS
import utils

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50      # ₹Cr (20-day avg)
STRANGLE_DTE    = 30      # days until expiry
ATR_WIDTH       = 1.2     # ±1.2×ATR strike width (wider)
POPCUT          = 0.60    # require ≥60% combined PoP (lower)
TOP_N_STRANG    = 10      # max strangle ideas
RSI_FALLBACK_N  = 5       # if no strangles, take top-5 RSI stocks
RSI_THRESHOLD   = 55

# ── EXPIRY FINDER ───────────────────────────────────────────────────────────
def next_expiry(days_out=STRANGLE_DTE):
    today = date.today()
    e = date(today.year, today.month, 28)
    while e.weekday() != 3:
        e -= timedelta(days=1)
    if (e - today).days < days_out:
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        e = date(y, m, 28)
        while e.weekday() != 3:
            e -= timedelta(days=1)
    return e

# ── Black–Scholes Δ & norm_CDF ──────────────────────────────────────────────
def norm_cdf(x): return (1 + math.erf(x / math.sqrt(2))) / 2
def bs_delta(spot, strike, dte, call=True, vol=0.25, r=0.05):
    t = dte / 365
    d1 = (math.log(spot/strike) + (r + 0.5*vol*vol)*t) / (vol*math.sqrt(t))
    return (math.exp(-r*t) * norm_cdf(d1)) if call else (-math.exp(-r*t) * norm_cdf(-d1))

def round_down(x, step): return int(x // step * step)
def round_up(x,   step): return int(math.ceil(x/step) * step)

# ── MAIN generator ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    strangles: List[Dict] = []

    # 1) Try short‐strangles
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue

        avg_turn = (df["close"] * df["volume"]).rolling(20).mean().iloc[-1] / 1e7
        if avg_turn < MIN_TURNOVER_CR:
            continue

        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df, 14).iloc[-1]
        width = ATR_WIDTH * atr14

        put_strike  = round_down(spot - width, 50)
        call_strike = round_up(spot + width, 50)

        exp = next_expiry()
        dte = (exp - date.today()).days

        delta_p = bs_delta(spot, put_strike,  dte, call=False)
        delta_c = bs_delta(spot, call_strike, dte, call=True)
        pop_p   = 1 - abs(delta_p)
        pop_c   = 1 - abs(delta_c)
        combo   = round(pop_p * pop_c, 2)

        if combo < POPCUT:
            continue

        strangles.append({
            "date":     today,
            "symbol":   sym,
            "strategy": "ShortStrangle",
            "entry":    0,
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

    # If we got any strangles, return top-N by PoP
    if strangles:
        return sorted(strangles, key=lambda t: t["pop"], reverse=True)[:TOP_N_STRANG]

    # 2) Fallback: top-RSI stocks
    rsi_list = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue
        r = utils.rsi(df, 14).iloc[-1]
        if r >= RSI_THRESHOLD:
            rsi_list.append((sym, r))

    rsi_list.sort(key=lambda x: x[1], reverse=True)
    fallback = []
    for sym, r in rsi_list[:RSI_FALLBACK_N]:
        price = df = utils.fetch_ohlc(sym, 1)["close"].iloc[-1]
        fallback.append({
            "date":     today,
            "symbol":   sym,
            "strategy": "RSI_Fallback",
            "entry":    price,
            "cmp":      price,
            "target":   round(price * 1.03, 2),
            "sl":       round(price * 0.98, 2),
            "pop":      None,
            "action":   "Buy",
            "notes":    {"rsi": r},
        })
    return fallback

