import json
from utils import fetch_cmp, generate_trade_signal

# ✅ NSE 100 Universe (you can extend this if needed)
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

    print(f"\n🚀 Starting Sniper Engine... Total symbols to scan: {len(NSE_100_SYMBOLS)}\n")

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
        else:
            print(f"⚠️ Skipped: {symbol} — Trade signal returned None")

    print(f"\n📊 Total Valid Trades: {len(valid_trades)}")
    print(f"❌ Failed Symbols: {failed}\n")

    return valid_trades, failed

def save_trades_to_json(trades):
    if not trades:
        print("⚠️ No valid trades to save to JSON.")
        return

    try:
        with open("trades.json", "w") as f:
            json.dump(trades, f, indent=2)
        print(f"✅ Saved {len(trades)} trades to trades.json\n")
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

def run_sniper_engine():
    trades, failed = generate_sniper_trades()

    # ✅ Log each trade before saving
    print("🔽 Final Trades to be Saved:")
    for t in trades:
        print(f"- {t['symbol']} | CMP: {t['cmp']} | Target: {t['target']} | SL: {t['sl']} | PoP: {t['pop']}")

    save_trades_to_json(trades)

if __name__ == "__main__":
    run_sniper_engine()
