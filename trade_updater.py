import json
from datetime import datetime

def update_trade_status(trades, latest_prices):
    updated = []

    for trade in trades:
        symbol = trade["symbol"].split()[0]  # 'CIPLA JUL FUT' → 'CIPLA'
        entry = trade["entry"]
        target = trade["target"]
        sl = trade["sl"]
        cmp = latest_prices.get(symbol)

        trade["status"] = "Open"
        trade["exit_date"] = "-"
        trade["holding"] = "-"
        trade["pnl"] = "-"
        trade["return_pct"] = "-"

        if cmp:
            pnl = cmp - entry
            return_pct = round((pnl / entry) * 100, 2)
            trade["return_pct"] = f"{return_pct}%"
            trade["pnl"] = f"{round(pnl, 2)}"

            if cmp >= target:
                trade["status"] = "Target Hit"
                trade["exit_date"] = datetime.now().strftime("%Y-%m-%d")
                trade["holding"] = (datetime.now() - datetime.strptime(trade["date"], "%Y-%m-%d")).days
            elif cmp <= sl:
                trade["status"] = "SL Hit"
                trade["exit_date"] = datetime.now().strftime("%Y-%m-%d")
                trade["holding"] = (datetime.now() - datetime.strptime(trade["date"], "%Y-%m-%d")).days

        updated.append(trade)

    return updated

def run_trade_updater():
    try:
        with open("trades.json", "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print("❌ trades.json not found.")
        return

    # 🔄 Replace this simulated CMP logic with Kite API or real feed soon
    latest_prices = {
        trade["symbol"].split()[0]: trade["entry"] * 1.01 for trade in trades
    }

    updated = update_trade_status(trades, latest_prices)

    with open("trades.json", "w") as f:
        json.dump(updated, f, indent=2)

    print(f"✅ {len(updated)} trades updated with status and P&L")

if __name__ == "__main__":
    run_trade_updater()
