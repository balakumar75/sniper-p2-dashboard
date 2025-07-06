import json
from datetime import datetime

TRADES_FILE = "data/trades.json"

def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)

def add_trade(new_trade):
    trades = load_trades()
    # Check if this trade already exists by symbol and date
    exists = any(t["symbol"] == new_trade["symbol"] and t["date"] == new_trade["date"] for t in trades)
    if not exists:
        new_trade["status"] = "Open"
        new_trade["holding_days"] = 0
        new_trade["exit_reason"] = ""
        trades.append(new_trade)
        save_trades(trades)

def update_trade_status(symbol, status, exit_reason=""):
    trades = load_trades()
    for t in trades:
        if t["symbol"] == symbol and t["status"] == "Open":
            t["status"] = status
            t["exit_reason"] = exit_reason
            t["exit_date"] = datetime.now().strftime("%Y-%m-%d")
    save_trades(trades)
