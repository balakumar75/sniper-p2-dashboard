from sniper_engine import generate_sniper_trades
import json
from datetime import datetime
import os

try:
    # Generate trades
    trades = generate_sniper_trades()
    formatted = []

    for trade in trades:
        trade["date"] = datetime.today().strftime("%Y-%m-%d")
        formatted.append(trade)

    # Save to trades.json
    output_path = os.path.join(os.path.dirname(__file__), "trades.json")
    with open(output_path, "w") as f:
        json.dump(formatted, f, indent=2)

    print(f"✅ {len(formatted)} trades written to trades.json")

except Exception as e:
    print("❌ ERROR in sniper_run_all.py:", e)
