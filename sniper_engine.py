"""
sniper_engine.py

Generates Options-Strangle ideas with strike & premium, skipping symbols without option tokens for the expiry.
"""
from typing import List, Dict
from datetime import date, timedelta
import math
import utils
from instruments import FNO_SYMBOLS

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50      # ₹Cr (20-day avg)
STRANGLE_DTE    = 30      # days until expiry
ATR_WIDTH       = 1.2     # ATR multiplier
POPCUT          = 0.60    # minimum PoP
TOP_N_STRANG    = 10      # max ideas

# ── EXPIRY finder ───────────────────────────────────────────────────────────
def next_expiry(days_out=STRANGLE_DTE) -> date:
    today = date.today()
    # find last Thursday of this month
    e = date(today.year, today.month, 28)
    while e.weekday() != 3:
        e -= timedelta(days=1)
    # if too soon, roll to next month
    if (e - today).days < days_out:
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        e = date(y, m, 28)
        while e.weekday() != 3:
            e -= timedelta(days=1)
    return e

# ── MAIN GENERATOR ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    ideas: List[Dict] = []

    # 1) Options-Strangles
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue

        # liquidity filter
        turn = utils.avg_turnover(df)
        if turn < MIN_TURNOVER_CR:
            continue

        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df, 14).iloc[-1]
        width = ATR_WIDTH * atr14

        put_strike  = math.floor((spot - width) / 50) * 50
        call_strike = math.ceil((spot + width) / 50) * 50

        exp = next_expiry()
        dte = (exp - date.today()).days

        # PoP combo via BS deltas
        dp    = utils.bs_delta(spot, put_strike,  dte, call=False)
        dc    = utils.bs_delta(spot, call_strike, dte, call=True)
        combo = round((1 - abs(dp)) * (1 - abs(dc)), 2)
        if combo < POPCUT:
            continue

        # fetch option tokens & premiums, skip if missing
        try:
            ptkn = utils.option_token(sym, put_strike, exp, "PE")
            ctkn = utils.option_token(sym, call_strike, exp, "CE")
        except KeyError:
            continue

        pp = utils.fetch_option_price(ptkn)
        cp = utils.fetch_option_price(ctkn)

        ideas.append({
            "date":        today,
            "symbol":      sym,
            "type":        "Options-Strangle",
            "put_strike":  put_strike,
            "call_strike": call_strike,
            "put_price":   round(pp, 2),
            "call_price":  round(cp, 2),
            "pop":         combo,
            "status":      "Open",
            "action":      "Sell",
        })

    # return top N
    return sorted(ideas, key=lambda x: x["pop"], reverse=True)[:TOP_N_STRANG]
