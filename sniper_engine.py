# sniper_engine.py

from datetime import date
from config import (
    FNO_SYMBOLS,
    RSI_MIN,
    ADX_MIN,
    VOL_MULTIPLIER,
    POPCUT,
    TOP_N_MOMENTUM,
)
import utils

def generate_sniper_trades() -> list[dict]:
    """
    Produces a combined list of trade-ideas:
     1) Cash-Momentum – top‐N names by RSI meeting ADX/volume filters
     2) Options‐Strangle – OTM strangles with PoP ≥ POPCUT
    """
    trades = []
    today = date.today().isoformat()

    # ── 1) Cash‐Momentum leg ────────────────────────────────────────────────
    momentum = []
    for sym in FNO_SYMBOLS:
        # must have enough history
        df = utils.fetch_ohlc(sym, 20)
        if df is None or df.empty:
            continue

        # filter by ADX
        adx = utils.fetch_adx(sym)
        if adx < ADX_MIN:
            continue

        # filter by volume (today’s volume vs 14‑day average)
        avg_vol = df["volume"].rolling(14).mean().iloc[-1]
        if df["volume"].iloc[-1] < VOL_MULTIPLIER * avg_vol:
            continue

        # compute RSI
        rsi = utils.fetch_rsi(sym, period=14)
        if rsi < RSI_MIN:
            continue

        # collect for ranking
        momentum.append((sym, rsi, df))

    # take top‐N by RSI
    momentum = sorted(momentum, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi, df in momentum:
        entry = df["close"].iloc[-1]
        trades.append({
            "Date":   today,
            "Symbol": sym,
            "Type":   "Cash-Momentum",
            "Entry":  round(entry, 2),
            "CMP":    round(entry, 2),
            "Target": None,
            "SL":     None,
            "PoP":    None,
            "Status": "Open",
            "P&L (₹)": None,
            "Action": "Buy",
        })

    # ── 2) Options‐Strangle leg ──────────────────────────────────────────────
    STRIKE_WIDTH = 50    # OTM distance
    LOOKBACK_DAYS = 90   # for PoP calculation
    EXPIRY = "2025-07-31"

    for sym in FNO_SYMBOLS:
        # get yesterday’s close
        df_spot = utils.fetch_ohlc(sym, 2)
        if df_spot is None or df_spot.empty:
            continue
        spot = df_spot["close"].iloc[-1]

        # determine ATM‐rounded strike (to nearest 100)
        interval = 100
        atm = round(spot / interval) * interval
        put_strike  = atm - STRIKE_WIDTH
        call_strike = atm + STRIKE_WIDTH

        # look up tokens
        ptkn = utils.option_token(sym, put_strike, EXPIRY, "PE")
        ctkn = utils.option_token(sym, call_strike, EXPIRY, "CE")
        if not ptkn or not ctkn:
            continue

        # fetch premiums
        prem_put  = utils.fetch_option_price(ptkn) or 0.0
        prem_call = utils.fetch_option_price(ctkn) or 0.0
        total_prem = round(prem_put + prem_call, 2)

        # compute historical PoP
        pop = utils.hist_pop(
            sym,
            tgt_pct=(STRIKE_WIDTH / spot) * 100,
            sl_pct=(STRIKE_WIDTH / spot) * 100,
            lookback_days=LOOKBACK_DAYS,
        )

        if pop >= POPCUT:
            trades.append({
                "Date":   today,
                "Symbol": sym,
                "Type":   f"Options-Strangle {put_strike}/{call_strike}",
                "Entry":  total_prem,
                "CMP":    total_prem,
                "Target": None,
                "SL":     None,
                "PoP":    pop,
                "Status": "Open",
                "P&L (₹)": None,
                "Action": "Sell",
            })

    return trades
