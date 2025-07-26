"""
sniper_engine.py

Generates a combined list of:
  1) Options-Strangle ideas (up to TOP_N_STRANG)
  2) Futures picks (up to TOP_N_FUTURES)
  3) Cash-Momentum fallbacks (up to TOP_N_MOMENTUM)

All three lists are concatenated and returned, sorted by their key metric.
"""
from typing import List, Dict
from datetime import date, timedelta
import math

import utils
import pandas as pd
from config import RSI_MIN, TOP_N_MOMENTUM, POPCUT
from instruments import FNO_SYMBOLS

# Strangle parameters
MIN_TURNOVER_CR = 50     # ₹Cr (20-day avg)
STRANGLE_DTE    = 30     # days until expiry
ATR_WIDTH       = 1.2
TOP_N_STRANG    = 10

# Futures parameters
TOP_N_FUTURES = 5

def next_expiry(days_out=STRANGLE_DTE) -> date:
    today = date.today()
    # find last Thursday of this month
    exp = date(today.year, today.month, 28)
    while exp.weekday() != 3:
        exp -= timedelta(days=1)
    # roll forward if too soon
    if (exp - today).days < days_out:
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        exp = date(y, m, 28)
        while exp.weekday() != 3:
            exp -= timedelta(days=1)
    return exp

def generate_sniper_trades() -> List[Dict]:
    today_str = date.today().isoformat()
    exp = next_expiry()
    dte = (exp - date.today()).days

    ideas: List[Dict] = []

    # 1) Options-Strangle
    strangles = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue
        if utils.avg_turnover(df) < MIN_TURNOVER_CR:
            continue

        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df, 14).iloc[-1]
        width = ATR_WIDTH * atr14

        put_strike  = math.floor((spot - width) / 50) * 50
        call_strike = math.ceil((spot + width) / 50) * 50

        dp = utils.bs_delta(spot, put_strike,  dte, call=False)
        dc = utils.bs_delta(spot, call_strike, dte, call=True)
        pop = round((1 - abs(dp)) * (1 - abs(dc)), 2)
        if pop < POPCUT:
            continue

        try:
            ptkn = utils.option_token(sym, put_strike, exp, "PE")
            ctkn = utils.option_token(sym, call_strike, exp, "CE")
        except KeyError:
            continue

        pp = utils.fetch_option_price(ptkn)
        cp = utils.fetch_option_price(ctkn)

        strangles.append({
            "date":        today_str,
            "symbol":      sym,
            "type":        "Options-Strangle",
            "put_strike":  put_strike,
            "call_strike": call_strike,
            "put_price":   round(pp, 2),
            "call_price":  round(cp, 2),
            "pop":         pop,
            "status":      "Open",
            "action":      "Sell",
        })

    # limit to top N by PoP
    strangles = sorted(strangles, key=lambda t: t["pop"], reverse=True)[:TOP_N_STRANG]
    ideas.extend(strangles)

    # 2) Futures (filter by RSI)
    futures = []
    for sym in FNO_SYMBOLS:
        rsi_val = utils.fetch_rsi(sym, 60)
        if rsi_val is None or rsi_val < RSI_MIN:
            continue
        try:
            fut_tkn = utils.future_token(sym, exp)
        except KeyError:
            continue
        price = utils.fetch_future_price(fut_tkn)
        futures.append({
            "date":   today_str,
            "symbol": sym,
            "type":   "Futures",
            "entry":  round(price, 2),
            "rsi":    round(rsi_val, 2),
            "status": "Open",
            "action": "Buy",
        })

    # limit and sort futures by RSI
    futures = sorted(futures, key=lambda t: t["rsi"], reverse=True)[:TOP_N_FUTURES]
    ideas.extend(futures)

    # 3) Cash-Momentum fallback
    mom = []
    for sym in FNO_SYMBOLS:
        rsi_val = utils.fetch_rsi(sym, 60)
        if rsi_val is None:
            continue
        pop_val = utils.hist_pop(sym, tgt_pct=2, sl_pct=1) or 0
        if pop_val < 0.5:
            continue
        mom.append((sym, rsi_val, pop_val))

    # select top by RSI
    mom_sorted = sorted(mom, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi_val, pop_val in mom_sorted:
        df = utils.fetch_ohlc(sym, 60)
        entry = df["close"].iloc[-1]
        sl    = entry * 0.99
        tgt   = entry * 1.02
        ideas.append({
            "date":   today_str,
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  round(entry, 2),
            "SL":     round(sl, 2),
            "Target": round(tgt, 2),
            "PoP":    round(pop_val, 2),
            "status": "Open",
            "action": "Buy",
        })

    # final sort: strangles by pop first, then futures by rsi, then momentum by pop
    # here we simply preserve group order but could merge-sort if desired
    return ideas
