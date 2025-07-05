from trades_auto import load_trades, update_trade_status
from kite_utils import get_live_price
from datetime import datetime

def check_exit():
    trades = load_trades()
    for trade in trades:
        if trade["status"] != "Open":
            continue
        cmp = get_live_price(trade["symbol"])
        sl = trade["sl"]
        tgt = trade["target"]
        entry = trade["entry_price"]

        if cmp <= sl:
            pnl = cmp - entry
            update_trade_status(trade["id"], cmp, datetime.today().strftime("%Y-%m-%d"), pnl, "SL Hit")
        elif cmp >= tgt:
            pnl = cmp - entry
            update_trade_status(trade["id"], cmp, datetime.today().strftime("%Y-%m-%d"), pnl, "Target Hit")
        else:
            entry_date = datetime.strptime(trade["entry_date"], "%Y-%m-%d")
            hold_days = trade.get("holding_days", 2)
            if (datetime.today() - entry_date).days >= hold_days:
                pnl = cmp - entry
                update_trade_status(trade["id"], cmp, datetime.today().strftime("%Y-%m-%d"), pnl, "Time Exit")