import json
import os

# Point to the local file written by the sniper engine
TRADES_FILE = "trades.json"

def load_trades():
    try:
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, "r", encoding="utf-8") as file:
                trades = json.load(file)
                if isinstance(trades, list) and trades:
                    return trades
                else:
                    print("⚠️ trades.json exists but is empty.")
                    return []
        else:
            print("⚠️ trades.json does not exist in the runtime environment.")
            return []
    except Exception as e:
        print(f"❌ Error reading trades.json: {e}")
        return []
