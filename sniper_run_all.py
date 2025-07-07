import json
import os
from datetime import datetime
from sniper_engine import generate_sniper_trades  # assumes you have this engine ready

# ✅ Step 1: Generate trades dynamically (fetches CMP, runs filters, etc.)
sniper_trades = generate_sniper_trades()

# ✅ Step 2: Format output with full column set
formatted_trades = []

for trade in sniper_trades:
    formatted_trades.append({
        "date": datetime.today().strftime("%Y-%m-%d"),
        "symbol": trade.get("symbol"),
        "type": trade.get("type"),
        "entry": trade.get("entry"),
        "cmp": trade.get("cmp"),
        "target": trade.get("target"),
        "sl": trade.get("sl"),
        "pop": trade.get("pop"),
        "action": trade.get("action"),
        "sector": trade.get("sector"),
        "tags": trade.get("tags", []),
        "trap_zone": trade.get("trap_zone"),
        "expiry": trade.get("expiry"),
        "status": trade.get("status", "Open"),
        "buy_date": trade.get("buy_date", datetime.today().strftime("%Y-%m-%d")),
        "exit_date": trade.get("exit_date", ""),
        "holding_days": trade.get("holding_days", 0),
        "pnl_abs": trade.get("pnl_abs", 0),
        "pnl_pct": trade.get("pnl_pct", 0),
        "vwap_flag": trade.get("vwap_flag", ""),
        "obv_flag": trade.get("obv_flag", ""),
        "macd_flag": trade.get("macd_flag", ""),
        "rsi": trade.get("rsi", ""),
        "adx": trade.get("adx", ""),
        "structure": trade.get("structure", ""),
        "ict_flag": trade.get("ict_flag", ""),
        "option_greeks": trade.get("option_greeks", {}),
        "strike_zone": trade.get("strike_zone", ""),
        "news_flag": trade.get("news_flag", "")
    })

# ✅ Step 3: Save to trades.json
output_path = os.path.join(os.path.dirname(__file__), "trades.json")
with open(output_path, "w") as f:
    json.dump(formatted_trades, f, indent=2)

print(f"✅ {len(formatted_trades)} sniper trades written to trades.json")
