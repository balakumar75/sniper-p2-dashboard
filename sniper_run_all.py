"""
sniper_engine.py
Strangles + RSI-with-PoP-fallback, no blanks in PoP
"""
from typing import List, Dict
from datetime import date, timedelta
import math

from instruments import FNO_SYMBOLS
import utils

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50      # ₹Cr
STRANGLE_DTE    = 30
ATR_WIDTH       = 1.2
POPCUT          = 0.60
TOP_N_STRANG    = 10
RSI_FALLBACK_N  = 5
SL_PCT          = 2.0
TGT_PCT         = 3.0

# ── EXPIRY finder ───────────────────────────────────────────────────────────
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
    return math.exp(-r*t) * norm_cdf(d1) if call else -math.exp(-r*t) * norm_cdf(-d1)

def round_down(x, step): return int(x // step * step)
def round_up(x,   step): return int(math.ceil(x/step) * step)

# ── MAIN generator ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    strangles: List[Dict] = []

    # 1) Generate naked short-strangles
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
            "date":    today,
            "symbol":  sym,
            "type":    "Options-Strangle",
            "entry":   0,
            "cmp":     round(spot, 2),
            "target":  0,
            "sl":      0,
            "pop":     combo,
            "status":  "Open",
            "pnl":     0.0,
            "action":  "Sell",
        })

    # 2) If we got any strangles, return top-N by PoP
    if strangles:
        return sorted(strangles, key=lambda t: t["pop"], reverse=True)[:TOP_N_STRANG]

    # 3) ELSE fallback to top-RSI stocks WITH PoP
    rsi_list: List[tuple[str,float]] = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue
        r_val = utils.rsi(df, 14).iloc[-1]
        rsi_list.append((sym, r_val))

    # sort & take top N
    rsi_list.sort(key=lambda x: x[1], reverse=True)
    fallback: List[Dict] = []
    for sym, r in rsi_list[:RSI_FALLBACK_N]:
        df1 = utils.fetch_ohlc(sym, 90)  # 90-day lookback
        pop_val = utils.hist_pop(df1, TGT_PCT, SL_PCT) or 0.0
        price   = df1["close"].iloc[-1] if df1 is not None and not df1.empty else None
        if price is None:
            continue
        fallback.append({
            "date":    today,
            "symbol":  sym,
            "type":    "Cash-Momentum",
            "entry":   round(price, 2),
            "cmp":     round(price, 2),
            "target":  round(price * (1+TGT_PCT/100), 2),
            "sl":      round(price * (1-SL_PCT/100), 2),
            "pop":     round(pop_val, 2),
            "status":  "Open",
            "pnl":     0.0,
            "action":  "Buy",
        })

    return fallback
