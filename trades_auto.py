import json
from datetime import datetime

TRADES_FILE = "data/trades.json"

def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)

def add_trade(trade):
    trades = load_trades()
    existing = next((t for t in trades if t["id"] == trade["id"]), None)
    if existing:
        return
    trade["entry_date"] = datetime.today().strftime("%Y-%m-%d")
    trade["status"] = "Open"
    trades.append(trade)
    save_trades(trades)

def update_trade_status(trade_id, exit_price, exit_date, pnl, status):
    trades = load_trades()
    for t in trades:
        if t["id"] == trade_id:
            t["exit_price"] = exit_price
            t["exit_date"] = exit_date
            t["status"] = status
            t["pnl"] = pnl
            break
    save_trades(trades)