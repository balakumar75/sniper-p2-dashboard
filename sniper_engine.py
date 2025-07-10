
import json
from utils import fetch_cmp, generate_trade_signal

NSE_100_SYMBOLS = [
    "CIPLA", "ICICIBANK", "RELIANCE", "TCS", "INFY", "HDFCBANK", "AXISBANK", "ITC",
    "SBIN", "BAJFINANCE", "LT", "SUNPHARMA", "TITAN", "WIPRO", "DRREDDY", "ASIANPAINT",
    "TATASTEEL", "JSWSTEEL", "HINDUNILVR", "BEL", "DLF", "POWERGRID", "NTPC",
    "EICHERMOT", "KOTAKBANK", "TATAMOTORS", "HCLTECH", "ADANIENT", "ADANIPORTS", "UPL",
    "INDUSINDBK", "DIVISLAB", "TECHM", "GRASIM", "ULTRACEMCO", "NESTLEIND", "MARUTI",
    "BAJAJFINSV", "COALINDIA", "BRITANNIA", "ICICIPRULI", "TATACONSUM", "DABUR",
    "GODREJCP", "PIDILITIND", "SHREECEM", "NAUKRI", "HAVELLS", "CHOLAFIN", "MUTHOOTFIN",
    "PEL", "SRF", "TORNTPHARM", "APOLLOHOSP", "GLAND", "CROMPTON", "BOSCHLTD", "TRENT",
    "DMART", "IRCTC", "MCX", "IEX", "GUJGASLTD", "ZEEL", "IDFCFIRSTB", "INDIAMART",
    "BANDHANBNK", "TATAPOWER", "PFC", "ONGC", "CONCOR", "ABB", "PAGEIND"
]

def generate_sniper_trades():
    valid_trades = []
    failed = []

    for symbol in NSE_100_SYMBOLS:
        print(f"🔍 Fetching CMP for: {symbol}")
        cmp = fetch_cmp(symbol)

        if cmp is None:
            print(f"❌ Failed to fetch CMP for: {symbol}")
            failed.append(symbol)
            continue

        trade = generate_trade_signal(symbol, cmp)
        if trade:
            print(f"✅ Trade generated: {symbol} @ {cmp}")
            valid_trades.append(trade)

    return valid_trades, failed

def save_trades_to_json(trades):
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)

def run_sniper_engine():
    trades, failed = generate_sniper_trades()
    save_trades_to_json(trades)
    print(f"✅ {len(trades)} sniper trades saved to trades.json.")
    if failed:
        print("⚠️ Failed to fetch CMP for:", ", ".join(failed))

if __name__ == "__main__":
    run_sniper_engine()
