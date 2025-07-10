import json
import os
from datetime import datetime

TRADES_FILE = "trades.json"
DATE_FORMAT = "%Y-%m-%d"

def run_trade_updater():
    try:
        with open(TRADES_FILE, "r", encoding="utf-8") as file:
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

        # Default status
        trade["status"] = "Open"
        trade["exit_date"] = "-"

        # Determine status only if cmp is present
        if cmp is not None and target is not None and sl is not None:
            if cmp >= target:
                trade["status"] = "Target Hit"
                trade["exit_date"] = today.strftime(DATE_FORMAT)
            elif cmp <= sl:
                trade["status"] = "SL Hit"
                trade["exit_date"] = today.strftime(DATE_FORMAT)

        # Holding Days
        entry_date = trade.get("date")
        if entry_date and entry_date != "-":
            try:
                entry_dt = datetime.strptime(entry_date, DATE_FORMAT)
                exit_dt = today if trade["exit_date"] != "-" else today
                trade["holding_days"] = (exit_dt - entry_dt).days
            except:
                trade["holding_days"] = "-"
        else:
            trade["holding_days"] = "-"

        # P&L & Return %
        if entry_price is not None and cmp is not None:
            pnl = round(cmp - entry_price, 2)
            trade["pnl"] = pnl
            try:
                return_pct = round((pnl / entry_price) * 100, 2)
                trade["return_pct"] = f"{return_pct}%"
            except ZeroDivisionError:
                trade["return_pct"] = "-"
        else:
            trade["pnl"] = "-"
            trade["return_pct"] = "-"

    # Save back to trades.json
    try:
        with open(TRADES_FILE, "w", encoding="utf-8") as file:
            json.dump(trades, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        print(f"✅ Trade status updated for {len(trades)} trades.")
    except Exception as e:
        print(f"❌ Failed to save updated trades: {e}")

if __name__ == "__main__":
    run_trade_updater()
