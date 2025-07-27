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
    Produces trade ideas:
      1) Cash‑Momentum with ATR‑based SL/Target
      2) Options‑Strangle with PoP filter
    """
    trades = []
    today = date.today().isoformat()

    # ── 1) Cash‑Momentum leg ────────────────────────────────────────────────
    momentum = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 20)
        if df is None or df.empty:
            continue

        # ADX filter
        adx = utils.fetch_adx(sym)
        if adx < ADX_MIN:
            continue

        # Volume filter
        avg_vol = df["volume"].rolling(14).mean().iloc[-1]
        if df["volume"].iloc[-1] < VOL_MULTIPLIER * avg_vol:
            continue

        # RSI filter
        rsi = utils.fetch_rsi(sym, period=14)
        if rsi < RSI_MIN:
            continue

        momentum.append((sym, rsi, df))

    # Top N by RSI
    top_mom = sorted(momentum, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi, df in top_mom:
        entry = df["close"].iloc[-1]
        # ATR-based SL/Target
        atr14        = utils.atr(df, 14).iloc[-1]
        sl_price     = round(entry - atr14, 2)
        target_price = round(entry + 2 * atr14, 2)

        trades.append({
            "Date":    today,
            "Symbol":  sym,
            "Type":    "Cash-Momentum",
            "Entry":   round(entry, 2),
            "CMP":     round(entry, 2),
            "Target":  target_price,
            "SL":      sl_price,
            "PoP":     None,
            "Status":  "Open",
            "P&L (₹)": None,
            "Action":  "Buy",
        })

    # ── 2) Options‑Strangle leg ───────────────────────────────────────────────
    STRIKE_WIDTH   = 50       # points OTM
    LOOKBACK_DAYS  = 90       # for PoP calc
    EXPIRY         = "2025-07-31"

    for sym in FNO_SYMBOLS:
        # Yesterday’s close as spot
        df_spot = utils.fetch_ohlc(sym, 2)
        if df_spot is None or df_spot.empty:
            continue
        spot = df_spot["close"].iloc[-1]

        # ATM‐rounded to nearest 100
        interval    = 100
        atm_strike  = round(spot / interval) * interval
        put_strike  = atm_strike - STRIKE_WIDTH
        call_strike = atm_strike + STRIKE_WIDTH

        # Lookup tokens
        ptkn = utils.option_token(sym, put_strike, EXPIRY, "PE")
        ctkn = utils.option_token(sym, call_strike, EXPIRY, "CE")
        if not ptkn or not ctkn:
            continue

        # Fetch premiums
        prem_put   = utils.fetch_option_price(ptkn)  or 0.0
        prem_call  = utils.fetch_option_price(ctkn)  or 0.0
        total_prem = round(prem_put + prem_call, 2)

        # Historical PoP
        pop = utils.hist_pop(
            sym,
            tgt_pct=(STRIKE_WIDTH/spot)*100,
            sl_pct=(STRIKE_WIDTH/spot)*100,
            lookback_days=LOOKBACK_DAYS,
        )

        if pop >= POPCUT:
            trades.append({
                "Date":    today,
                "Symbol":  sym,
                "Type":    f"Options‑Strangle {put_strike}/{call_strike}",
                "Entry":   total_prem,
                "CMP":     total_prem,
                "Target":  None,
                "SL":      None,
                "PoP":     pop,
                "Status":  "Open",
                "P&L (₹)": None,
                "Action":  "Sell",
            })

    return trades
