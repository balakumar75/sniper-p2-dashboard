import json
import os
from datetime import datetime
from kiteconnect import KiteConnect

# Load API credentials
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def fetch_live_cmp(symbol):
    try:
        instrument = f"NSE:{symbol}"
        quote = kite.ltp(instrument)
        return quote[instrument]['last_price']
    except Exception as e:
        print(f"❌ Error fetching CMP for {symbol}: {e}")
        return None

def update_trade_status(trades):
    updated_trades = []

    for trade in trades:
        base_symbol = trade["symbol"].split()[0]
        entry = trade["entry"]
        target = trade["target"]
        sl = trade["sl"]
        trade_date = trade.get("date", datetime.today().strftime("%Y-%m-%d"))
        cmp = fetch_live_cmp(base_symbol)

        if cmp is None:
            trade["status"] = "Open"
            trade["pnl"] = "-"
            trade["return_pct"] = "-"
            trade["cmp"] = "-"
            trade["cmp_updated"] = "-"
        else:
            pnl_amount = round((cmp - entry), 2)
            return_pct = round((cmp - entry) / entry * 100, 2)
            trade["cmp"] = cmp
            trade["cmp_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            trade["return_pct"] = return_pct

            if cmp >= target:
                trade["status"] = "Target Hit"
                trade["exit_date"] = datetime.today().strftime("%Y-%m-%d")
                holding_days = (datetime.today() - datetime.strptime(trade_date, "%Y-%m-%d")).days
                trade["holding"] = holding_days
                trade["pnl"] = round((target - entry), 2)
            elif cmp <= sl:
                trade["status"] = "SL Hit"
                trade["exit_date"] = datetime.today().strftime("%Y-%m-%d")
                holding_days = (datetime.today() - datetime.strptime(trade_date, "%Y-%m-%d")).days
                trade["holding"] = holding_days
                trade["pnl"] = round((sl - entry), 2)
            else:
                trade["status"] = "Open"
                trade["pnl"] = pnl_amount
                trade["holding"] = "-"
                trade["exit_date"] = "-"

        updated_trades.append(trade)

    return updated_trades

def run_trade_updater():
    try:
        with open("trades.json", "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print("❌ trades.json not found.")
        return

    updated_trades = update_trade_status(trades)

    with open("trades.json", "w") as f:
        json.dump(updated_trades, f, indent=2)

    print(f"✅ Updated {len(updated_trades)} trades with CMP, status, and return %.")

if __name__ == "__main__":
    run_trade_updater()
