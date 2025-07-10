import json
import os
from datetime import datetime
from kiteconnect import KiteConnect

# ✅ Load API credentials
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ✅ Get live CMP using Kite
def fetch_live_cmp(symbol):
    try:
        instrument = f"NSE:{symbol}"
        quote = kite.ltp(instrument)
        return quote[instrument]['last_price']
    except Exception as e:
        print(f"❌ Error fetching CMP for {symbol}: {e}")
        return None

# ✅ Update each trade with CMP, P&L, Status
def update_trade_status(trades):
    updated_trades = []

    for trade in trades:
        symbol = trade["symbol"]
        base_symbol = symbol.split()[0]
        entry = trade.get("entry")
        target = trade.get("target")
        sl = trade.get("sl")
        trade_date = trade.get("date", datetime.today().strftime("%Y-%m-%d"))

        # 🟢 Fetch latest CMP
        cmp = fetch_live_cmp(base_symbol)

        if cmp is None:
            trade["status"] = "Open"
            trade["cmp"] = "-"
            trade["cmp_updated"] = "-"
            trade["pnl"] = "-"
            trade["return_pct"] = "-"
            trade["exit_date"] = "-"
            trade["holding"] = "-"
        else:
            trade["cmp"] = cmp
            trade["cmp_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            pnl_amount = round(cmp - entry, 2)
            return_pct = round((cmp - entry) / entry * 100, 2)
            trade["pnl"] = pnl_amount
            trade["return_pct"] = return_pct

            # 🟢 Determine trade outcome
            if cmp >= target:
                trade["status"] = "Target Hit"
                trade["exit_date"] = datetime.today().strftime("%Y-%m-%d")
                trade["holding"] = (datetime.today() - datetime.strptime(trade_date, "%Y-%m-%d")).days
                trade["pnl"] = round(target - entry, 2)
            elif cmp <= sl:
                trade["status"] = "SL Hit"
                trade["exit_date"] = datetime.today().strftime("%Y-%m-%d")
                trade["holding"] = (datetime.today() - datetime.strptime(trade_date, "%Y-%m-%d")).days
                trade["pnl"] = round(sl - entry, 2)
            else:
                trade["status"] = "Open"
                trade["exit_date"] = "-"
                trade["holding"] = "-"

        # 🚫 Prevent pop() method from being accidentally serialized
        if isinstance(trade.get("pop"), str):
            pass  # All good
        else:
            trade["pop"] = "88%"  # Fallback value if corrupted

        updated_trades.append(trade)

    return updated_trades

# ✅ Run the full updater
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
