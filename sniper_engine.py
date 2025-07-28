# sniper_engine.py

from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

def generate_sniper_trades() -> list[dict]:
    trades = []
    today  = date.today().isoformat()

    print("⚙️  Debug: RSI / ADX / Vol / ATR for each symbol")

    scores = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=30)
        if df is None or df.empty:
            continue

        rsi = utils.fetch_rsi(sym, period=14)
        adx = utils.fetch_adx(sym, period=14)
        atr = utils.fetch_atr(sym, period=14)
        vol = int(df["volume"].iloc[-1])

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  ATR={atr:6.2f}  Vol={vol:,}")

        scores.append((sym, rsi, df, atr))

    # pick top N by RSI
    for sym, rsi, df, atr in sorted(scores, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]:
        entry = float(round(df["close"].iloc[-1], 2))
        sl    = float(round(entry - atr, 2))
        tgt   = float(round(entry + atr, 2))

        trades.append({
            "date":   today,
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  entry,
            "cmp":    entry,
            "target": tgt,
            "sl":     sl,
            "pop":    None,
            "status": "Open",
            "pnl":    None,
            "action": "Buy",
        })

    # … your Options‑Strangle block if you still want it, unchanged …

    return trades
