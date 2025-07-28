# sniper_engine.py

from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

def generate_sniper_trades() -> list[dict]:
    """
    1) Debug-print RSI/ADX/Vol for each symbol
    2) Pick top-N by RSI for cash momentum
    3) (Optional) Append options-strangle legs
    All output keys are lowercase to match dashboard JS.
    """
    trades = []
    today = date.today().isoformat()

    print("⚙️  Debug: RSI / ADX / Vol for each symbol")

    # ── 1) Cash‑Momentum ─────────────────────────────────────────────────────
    momentum = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 30)
        if df is None or df.empty:
            continue

        rsi     = utils.fetch_rsi(sym, period=14)
        adx     = utils.fetch_adx(sym, period=14)
        curr_v  = int(df["volume"].iloc[-1])
        avg_v   = int(df["volume"].rolling(14).mean().iloc[-1])

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  Vol={curr_v:,} (avg {avg_v:,})")

        momentum.append((sym, rsi, df))

    # pick top‑N by RSI
    top_mom = sorted(momentum, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi, df in top_mom:
        price = float(round(df["close"].iloc[-1], 2))
        trades.append({
            "date":   today,
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  price,
            "cmp":    price,
            "target": None,
            "sl":     None,
            "pop":    None,
            "status": "Open",
            "pnl":    None,
            "action": "Buy",
        })

    # ── 2) Options‑Strangle ─────────────────────────────────────────────────
    # (you can comment out this block if you just want to debug cash leg)
    STRIKE_WIDTH  = 50
    LOOKBACK_DAYS = 90
    EXPIRY        = "2025-07-31"

    for sym in FNO_SYMBOLS:
        df2 = utils.fetch_ohlc(sym, 2)
        if df2 is None or df2.empty:
            continue
        spot = df2["close"].iloc[-1]

        # Round to nearest 100 for ATM
        atm         = round(spot / 100) * 100
        put_strike  = atm - STRIKE_WIDTH
        call_strike = atm + STRIKE_WIDTH

        ptkn = utils.option_token(sym, put_strike, EXPIRY, "PE")
        ctkn = utils.option_token(sym, call_strike,EXPIRY, "CE")
        if not ptkn or not ctkn:
            continue

        pu = utils.fetch_option_price(ptkn) or 0.0
        pc = utils.fetch_option_price(ctkn) or 0.0
        prem = float(round(pu + pc, 2))

        pop = float(utils.hist_pop(
            sym,
            tgt_pct=(STRIKE_WIDTH/spot)*100,
            sl_pct =(STRIKE_WIDTH/spot)*100,
            lookback_days=LOOKBACK_DAYS,
        ) or 0.0)

        trades.append({
            "date":   today,
            "symbol": sym,
            "type":   f"Options-Strangle {put_strike}/{call_strike}",
            "entry":  prem,
            "cmp":    prem,
            "target": None,
            "sl":     None,
            "pop":    pop,
            "status": "Open",
            "pnl":    None,
            "action": "Sell",
        })

    return trades
