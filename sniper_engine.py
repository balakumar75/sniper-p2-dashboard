# sniper_engine.py

from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

def generate_sniper_trades() -> list[dict]:
    trades = []
    today = date.today().isoformat()

    print("⚙️  Debug: RSI / ADX / Vol for each symbol")

    momentum = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 30)
        if df is None or df.empty:
            continue

        # use our new Wilder RSI & ADX
        rsi = utils.fetch_rsi(sym, period=14)
        adx = utils.fetch_adx(sym, period=14)
        curr_vol = df["volume"].iloc[-1]
        avg_vol  = df["volume"].rolling(14).mean().iloc[-1]

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  Vol={curr_vol:,.0f} (avg {avg_vol:,.0f})")

        momentum.append((sym, rsi, df))

    # take top N by RSI
    top_mom = sorted(momentum, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]
    for sym, rsi, df in top_mom:
        price = df["close"].iloc[-1]
        trades.append({
            "Date":    today,
            "Symbol":  sym,
            "Type":    "Cash-Momentum",
            "Entry":   float(round(price, 2)),
            "CMP":     float(round(price, 2)),
            "Target":  None,
            "SL":      None,
            "PoP":     None,
            "Status":  "Open",
            "P&L (₹)": None,
            "Action":  "Buy",
        })

    # (You can keep your Options‑Strangle block here or comment it out for now.)

    return trades
