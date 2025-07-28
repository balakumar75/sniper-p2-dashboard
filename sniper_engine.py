# sniper_engine.py

from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

def generate_sniper_trades() -> list[dict]:
    trades = []
    today = date.today().isoformat()

    print("⚙️  Debug: fetching RSI / ADX / Vol (100d lookback) for each symbol")

    # 1) Cash‑Momentum only
    scores = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=30)
        if df is None or df.empty:
            continue

        rsi = utils.fetch_rsi(sym, period=14)
        adx = utils.fetch_adx(sym, period=14)
        vol = int(df["volume"].iloc[-1])

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  Vol={vol:,}")

        scores.append((sym, rsi, df))

    # pick top N by RSI
    for sym, rsi, df in sorted(scores, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]:
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

    # 🚧 OPTIONS‑STRANGLE BLOCK SKIPPED FOR NOW 🚧

    return trades
