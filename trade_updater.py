import json
from datetime import datetime, date

def update_trade_status(trades, latest_prices):
    updated_trades = []

    for trade in trades:
        symbol = trade["symbol"].split()[0]
        entry = trade["entry"]
        target = trade["target"]
        sl = trade["sl"]
        action = trade.get("action", "Buy")

        # Date and Holding
        trade_date = datetime.strptime(trade.get("date", str(date.today())), "%Y-%m-%d").date()
        today = date.today()
        holding_days = (today - trade_date).days

        cmp = latest_prices.get(symbol)

        if cmp is None:
            status = "Open"
            pnl = "-"
            return_pct = "-"
        else:
            if action == "Buy":
                if cmp >= target:
                    status = "Target Hit"
                    pnl = cmp - entry
                    return_pct = f"{round(((cmp - entry) / entry) * 100, 2)}%"
                elif cmp <= sl:
                    status = "SL Hit"
                    pnl = cmp - entry
                    return_pct = f"{round(((cmp - entry) / entry) * 100, 2)}%"
                else:
                    status = "Open"
                    pnl = cmp - entry
                    return_pct = f"{round(((cmp - entry) / entry) * 100, 2)}%"
            else:
                # For short trades (Sell)
                if cmp <= target:
                    status = "Target Hit"
                    pnl = entry - cmp
                    return_pct = f"{round(((entry - cmp) / entry) * 100, 2)}%"
                elif cmp >= sl:
                    status = "SL Hit"
                    pnl = entry - cmp
                    return_pct = f"{round(((entry - cmp) / entry) * 100, 2)}%"
                else:
                    status = "Open"
                    pnl = entry - cmp
                    return_pct = f"{round(((entry - cmp) / entry) * 100, 2)}%"

        # Finalize trade
        trade.update({
            "status": status,
            "cmp": cmp if cmp is not None else "-",
            "pnl": f"{round(pnl, 2)}" if isinstance(pnl, (int, float)) else pnl,
            "return_pct": return_pct,
            "holding": holding_days,
            "exit_date": today.strftime("%Y-%m-%d") if status != "Open" else "-"
        })

        updated_trades.append(trade)

    return updated_trades


def run_trade_updater():
    try:
        with open("trades.json", "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print("❌ trades.json not found.")
        return

    # Simulated CMP (replace this with real API if needed)
    latest_prices = {
        trade["symbol"].split()[0]: trade["entry"] * 1.008 for trade in trades
    }

    updated_trades = update_trade_status(trades, latest_prices)

    with open("trades.json", "w") as f:
        json.dump(updated_trades, f, indent=2)

    print(f"✅ Updated {len(updated_trades)} trades with CMP, P&L, status, and holding days.")

if __name__ == "__main__":
    run_trade_updater()
