# sniper_engine.py

from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

def generate_sniper_trades() -> list[dict]:
    """
    Cash‑Momentum: top‑N by RSI with ATR‑based SL/Target, stamped with entry_date.
    """
    trades = []
    entry_today = date.today().isoformat()

    print("⚙️  Debug: RSI / ADX / ATR / CMP for each symbol")

    stats = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=40)
        if df is None or df.empty:
            continue

        rsi = utils.fetch_rsi(sym, period=14)
        adx = utils.fetch_adx(sym, period=14)
        atr = utils.fetch_atr(sym, period=14)
        cmp = float(df["close"].iloc[-1])

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  ATR={atr:6.2f}  CMP={cmp:.2f}")

        stats.append((sym, rsi, df, atr))

    # pick top N by RSI
    for sym, rsi, df, atr in sorted(stats, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]:
        entry = float(round(df["close"].iloc[-1], 2))
        sl    = float(round(entry - atr, 2))
        tgt   = float(round(entry + atr, 2))

        trades.append({
            "entry_date": entry_today,
            "symbol":     sym,
            "type":       "Cash-Momentum",
            "entry":      entry,
            "cmp":        entry,
            "target":     tgt,
            "sl":         sl,
            "pop":        None,
            "status":     "Open",
            "pnl":        None,
            "action":     "Buy",
            # exit_date will be added by monitor_trades.py when closed
        })

    return trades
