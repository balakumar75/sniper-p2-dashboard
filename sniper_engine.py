"""
sniper_engine.py

Generates Options-Strangle ideas with strikes & premiums.
"""
from typing import List, Dict
from datetime import date, timedelta
import math
import utils
from instruments import FNO_SYMBOLS

# Parameters
MIN_TURNOVER_CR = 50
STRANGLE_DTE    = 30
ATR_WIDTH       = 1.2
POPCUT          = 0.60
TOP_N_STRANG    = 10

def next_expiry(days_out=STRANGLE_DTE):
    today = date.today()
    e = date(today.year, today.month, 28)
    while e.weekday() != 3: e -= timedelta(days=1)
    if (e - today).days < days_out:
        m = today.month + 1
        y = today.year + (m//13)
        e = date(y, m if m<=12 else 1, 28)
        while e.weekday() != 3: e -= timedelta(days=1)
    return e

def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    ideas = []

    # 1) Options-Strangles
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty: continue

        turn = utils.avg_turnover(df)
        if turn < MIN_TURNOVER_CR: continue

        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df, 14).iloc[-1]
        width = ATR_WIDTH * atr14

        put_strike  = math.floor((spot - width)/50)*50
        call_strike = math.ceil((spot + width)/50)*50

        exp = next_expiry()
        dte = (exp - date.today()).days

        # PoP combo
        dp    = utils.bs_delta(spot, put_strike,  dte, call=False)
        dc    = utils.bs_delta(spot, call_strike, dte, call=True)
        combo = round((1-abs(dp)) * (1-abs(dc)), 2)
        if combo < POPCUT: continue

        # fetch premiums
        ptkn = utils.option_token(sym, put_strike, exp, "PE")
        ctkn = utils.option_token(sym, call_strike, exp, "CE")
        pp   = utils.fetch_option_price(ptkn)
        cp   = utils.fetch_option_price(ctkn)

        ideas.append({
            "date":         today,
            "symbol":       sym,
            "type":         "Options-Strangle",
            "put_strike":   put_strike,
            "call_strike":  call_strike,
            "put_price":    round(pp, 2),
            "call_price":   round(cp, 2),
            "pop":          combo,
            "status":       "Open",
            "action":       "Sell",
        })

    return sorted(ideas, key=lambda x: x["pop"], reverse=True)[:TOP_N_STRANG]
