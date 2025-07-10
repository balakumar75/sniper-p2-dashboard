import json
from datetime import datetime
from utils import fetch_cmp  # make sure this exists and works

TRADES_FILE = "trades.json"
DATE_FORMAT = "%Y-%m-%d"

def generate_sniper_trades():
    print("🚀 Sniper Engine Started...")

    # Dummy list of stocks — replace with real F&O list if available
    symbols = ["HDFCLIFE", "SBIN", "RELIANCE"]

    trades = []

    for symbol in symbols:
        print(f"🔍 Checking {symbol}...")
        try:
            cmp = fetch_cmp(symbol)
            entry = cmp
            target = round(entry * 1.02, 2)
            sl = round(entry * 0.975, 2)

            trade = {
                "date": datetime.today().strftime(DATE_FORMAT),
                "symbol": symbol,
                "type": "Cash",
                "entry": entry,
                "cmp": cmp,
                "target": target,
                "sl": sl,
                "pop": "80%",
                "action": "Buy",
                "sector": "Neutral",
                "tags": ["RSI✅", "MACD✅", "ADX✅"],
                "status": "Open",
                "exit_date": "-",
                "holding_days": 0,
                "pnl": 0.0,
                "return_pct": "0%"
            }

            trades.append(trade)

        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

    return trades

def save_trades_to_json(trades):
    try:
        with open(TRADES_FILE, "w", encoding="utf-8") as f:
            json.dump(trades, f, indent=2)
        print(f"✅ Saved {len(trades)} trades to {TRADES_FILE}")
    except Exception as e:
        print(f"❌ Failed to save trades: {e}")
