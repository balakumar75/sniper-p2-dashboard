# sniper_engine.py

from datetime import date
from config import (
    FNO_SYMBOLS,
    TOP_N_MOMENTUM,
)
import utils

def generate_sniper_trades() -> list[dict]:
    """
    DEBUG SANITY‑CHECK: prints RSI/ADX/Vol for each symbol,
    then picks top‑10 by RSI unfiltered.
    """
    trades = []
    today = date.today().isoformat()

    print("⚙️  Sanity‑check mode: showing RSI / ADX / Vol for each symbol")

    # 1) Cash‑Momentum leg (debug: no filters)
    momentum = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 20)
        if df is None or df.empty:
            continue

        # fetch raw metrics
        adx      = utils.fetch_adx(sym) or 0.0
        rsi      = utils.fetch_rsi(sym, period=14) or 0.0
        avg_vol  = df["volume"].rolling(14).mean().iloc[-1]
        curr_vol = df["volume"].iloc[-1]

        # print for debugging
        print(f"  • {sym:12s}  RSI={rsi:5.1f}  ADX={adx:5.1f}  Vol={curr_vol:,.0f} (avg {avg_vol:,.0f})")

        # collect all for ranking
        momentum.append((sym, rsi, df))

    # take top N by RSI (debug: TOP_N_MOMENTUM = 10)
    top_mom = sorted(momentum, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi, df in top_mom:
        entry = df["close"].iloc[-1]
        # Basic Cash‑Momentum output (no SL/Target in debug)
        trades.append({
            "Date":    today,
            "Symbol":  sym,
            "Type":    "Cash-Momentum",
            "Entry":   round(entry, 2),
            "CMP":     round(entry, 2),
            "Target":  None,
            "SL":      None,
            "PoP":     None,
            "Status":  "Open",
            "P&L (₹)": None,
            "Action":  "Buy",
        })

    # 2) Options‑Strangle leg (unchanged, but POPCUT=0 so picks all)
    STRIKE_WIDTH   = 50
    LOOKBACK_DAYS  = 90
    EXPIRY         = "2025-07-31"

    for sym in FNO_SYMBOLS:
        df_spot = utils.fetch_ohlc(sym, 2)
        if df_spot is None or df_spot.empty:
            continue
        spot = df_spot["close"].iloc[-1]

        # ATM rounded
        interval    = 100
        atm_strike  = round(spot / interval) * interval
        put_strike  = atm_strike - STRIKE_WIDTH
        call_strike = atm_strike + STRIKE_WIDTH

        # lookup tokens
        ptkn = utils.option_token(sym, put_strike, EXPIRY, "PE")
        ctkn = utils.option_token(sym, call_strike, EXPIRY, "CE")
        if not ptkn or not ctkn:
            continue

        # premiums
        prem_put   = utils.fetch_option_price(ptkn) or 0.0
        prem_call  = utils.fetch_option_price(ctkn) or 0.0
        total_prem = round(prem_put + prem_call, 2)

        # historical PoP (debug: POPCUT=0 so always true)
        pop = utils.hist_pop(
            sym,
            tgt_pct=(STRIKE_WIDTH/spot)*100,
            sl_pct=(STRIKE_WIDTH/spot)*100,
            lookback_days=LOOKBACK_DAYS,
        ) or 0.0

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
