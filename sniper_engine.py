import json
from datetime import datetime

def run_sniper_system():
    print("🔍 Simulating sniper trade engine...")

    sample_trades = [
        {
            "symbol": "RELIANCE JUL FUT",
            "entry_price": 2750.0,
            "cmp": 2765.5,
            "sl": 2710.0,
            "target": 2800.0,
            "pop": 85,
            "status": "Open",
            "action": "Hold",
            "sector": "Energy",
            "expiry": "July Monthly",
            "buy_date": datetime.today().strftime("%Y-%m-%d")
        },
        {
            "symbol": "LTIM JUL FUT",
            "entry_price": 5050.0,
            "cmp": 5085.0,
            "sl": 4980.0,
            "target": 5150.0,
            "pop": 82,
            "status": "Open",
            "action": "Hold",
            "sector": "IT",
            "expiry": "July Monthly",
            "buy_date": datetime.today().strftime("%Y-%m-%d")
        }
    ]

    with open("trades.json", "w") as f:
        json.dump(sample_trades, f, indent=4)
        print("✅ Trades written to trades.json")
