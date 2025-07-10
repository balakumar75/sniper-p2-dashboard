import json
from datetime import datetime

TRADES_FILE = "trades.json"
DATE_FORMAT = "%Y-%m-%d"

def run_trade_updater():
    try:
        with open(TRADES_FILE, 'r') as file:
            trades = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No valid trades.json found.")
        return

    today = datetime.today()

    for trade in trades:
        entry_price = trade.get("entry")
        cmp = trade.get("cmp")
        target = trade.get("target")
        sl = trade.get("sl")

        # Skip if CMP is missing
        if cmp is None:
            trade["status"] = "Open"
            continue

        # Determine status
        if cmp >= target:
            trade["status"] = "Target Hit"
            trade["exit_date"] = today.strftime(DATE_FORMAT)
        elif cmp <= sl:
            trade["status"] = "SL Hit"
            trade["exit_date"] = today.strftime(DATE_FORMAT)
        else:
            trade["status"] = "Open"
            trade["exit_date"] = "-"

        # Holding Days
        entry_date = trade.get("date")
        if entry_date and entry_date != "-":
            try:
                entry_dt = datetime.strptime(entry_date, DATE_FORMAT)
                exit_dt = today if trade["status"] != "Open" else today
                trade["holding_days"] = (exit_dt - entry_dt).days
            except:
                trade["holding_days"] = "-"
        else:
            trade["holding_days"] = "-"

        # P&L calculation
        if cmp and entry_price:
            pnl = round(cmp - entry_price, 2)
            trade["pnl"] = pnl
            trade["return_pct"] = f"{round((pnl / entry_price) * 100, 2)}%"
        else:
            trade["pnl"] = "-"
            trade["return_pct"] = "-"

    # Save updated trades
    with open(TRADES_FILE, 'w') as file:
        json.dump(trades, file, indent=2)

    print(f"✅ Trade status updated for {len(trades)} trades.")
