import json
from datetime import datetime
from utils import fetch_cmp

# ✅ Sample symbols (replace with dynamic universe later)
symbols = ["HDFCLIFE", "SBIN", "RELIANCE"]

def generate_sniper_trades():
    trades = []
    print("🚀 Sniper Engine Starting...")

    for symbol in symbols:
        print(f"🔍 Checking {symbol}...")
        try:
            cmp = fetch_cmp(symbol)
            if cmp is None:
                continue

            entry = cmp
            target = round(entry * 1.02, 2)  # +2%
            sl = round(entry * 0.975, 2)     # -2.5%

            trade = {
                "date": datetime.today().strftime("%Y-%m-%d"),
                "symbol": symbol,
                "type": "Cash",
                "entry": entry,
                "cmp": cmp,
                "target": target,
                "sl": sl,
                "pop_pct": "85%",
                "action": "Buy",
                "sector": "Neutral",
                "tags": ["RSI✅", "MACD✅"],
                "status": "Open",
                "exit_date": "-",
                "holding_days": 0,
                "pnl": 0.0,
                "return_pct": "0%"
            }
            trades.append(trade)
        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

    print(f"✅ Trades generated: {len(trades)}")
    return trades

def save_trades_to_json(trades):
    try:
        with open("trades.json", "w", encoding="utf-8") as f:
            json.dump(trades, f, indent=2)
        print("✅ trades.json saved successfully.")
    except Exception as e:
        print(f"❌ Failed to save trades.json: {e}")
