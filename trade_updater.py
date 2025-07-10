import json
from datetime import datetime

def update_trade_status(trades, latest_prices):
    updated_trades = []

    for trade in trades:
        symbol = trade["symbol"].split()[0]  # Extract base symbol
        entry = trade["entry"]
        target = trade["target"]
        sl = trade["sl"]

        cmp = latest_prices.get(symbol)
        if cmp is None:
            trade["status"] = "Open"
            trade["pnl"] = "-"
        else:
            # Determine status and P&L
            if cmp >= target:
                trade["status"] = "Target Hit"
                trade["pnl"] = f"{round(((target - entry) / entry) * 100, 2)}%"
            elif cmp <= sl:
                trade["status"] = "SL Hit"
                trade["pnl"] = f"{round(((sl - entry) / entry) * 100, 2)}%"
            else:
                trade["status"] = "Open"
                trade["pnl"] = f"{round(((cmp - entry) / entry) * 100, 2)}%"

        updated_trades.append(trade)

    return updated_trades

def run_trade_updater():
    try:
        with open("trades.json", "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print("❌ trades.json not found.")
        return

    # Simulate live CMP (replace with Kite API or other feed)
    latest_prices = {
        trade["symbol"].split()[0]: trade["entry"] * 1.01 for trade in trades
    }

    updated_trades = update_trade_status(trades, latest_prices)

    with open("trades.json", "w") as f:
        json.dump(updated_trades, f, indent=2)

    print(f"✅ Updated {len(updated_trades)} trades with CMP status.")

if __name__ == "__main__":
    run_trade_updater()
