import json
import os
from datetime import datetime

TRADES_FILE = "data/trades.json"

def load_trades():
    if not os.path.exists(TRADES_FILE):
        return []
    with open(TRADES_FILE, "r") as f:
        return json.load(f)

def save_trade(trade):
    trades = load_trades()
    trade["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trades.append(trade)
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)

def get_all_trades():
    return load_trades()
