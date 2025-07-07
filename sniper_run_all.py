from trades import SNIPER_TRADES
import json
from datetime import datetime
import os

# ✅ Create a standard JSON structure
def format_trade(trade):
    return {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": trade.get("symbol", ""),
        "type": trade.get("type", ""),
        "entry": trade.get("entry", ""),
        "cmp": trade.get("cmp", ""),
        "target": trade.get("target", ""),
        "sl": trade.get("sl", ""),
        "pop": trade.get("pop", ""),
        "action": trade.get("action", ""),
        "sector": trade.get("sector", ""),
        "tags": trade.get("tags", []),
        "trap_zone": trade.get("trap_zone", ""),
        "expiry": trade.get("expiry", ""),
        "status": trade.get("status", "Open")
    }

# ✅ Format all trades
formatted_trades = [format_trade(trade) for trade in SNIPER_TRADES]

# ✅ Save to JSON
output_path = os.path.join(os.path.dirname(__file__), "trades.json")

with open(output_path, "w") as f:
    json.dump(formatted_trades, f, indent=2)

print(f"✅ {len(formatted_trades)} trades exported to trades.json")
