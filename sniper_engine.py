"""
Sniper Engine – generates trades with Exit-Date support.
"""

import json
from datetime import datetime
from config import FNO_SYMBOLS, DEFAULT_POP
from utils  import fetch_cmp, fetch_rsi, fetch_macd, fetch_adx, fetch_volume, \
                   fetch_sector_strength, fetch_option_chain

def generate_sniper_trades():
    trades = []
    print("🚀 Sniper Engine v3.1 – scanning universe…")

    for symbol in FNO_SYMBOLS:
        cmp_ = fetch_cmp(symbol)
        if cmp_ is None:                       # failed CMP fetch
            continue

        # simplified filters for brevity …
        if fetch_rsi(symbol) < 55: continue

        entry  = cmp_
        target = round(entry * 1.02, 2)
        sl     = round(entry * 0.975, 2)

        trade = {
            "date":        datetime.today().strftime("%Y-%m-%d"),
            "symbol":      symbol,
            "type":        "Cash",
            "entry":       entry,
            "cmp":         cmp_,
            "target":      target,
            "sl":          sl,
            "pop_pct":     DEFAULT_POP,
            "action":      "Buy",
            "sector":      fetch_sector_strength(symbol),
            "tags":        ["RSI✅"],
            "status":      "Open",
            "exit_date":   "-",               # <─ NEW column default
            "pnl":         0.0
        }
        trades.append(trade)

    print(f"✅ Total valid trades: {len(trades)}")
    return trades

def save_trades_to_json(trades):
    with open("trades.json", "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2)
    print("💾 trades.json saved.")

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
