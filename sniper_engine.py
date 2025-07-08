import json
import datetime
from utils import fetch_cmp, generate_trade_signal

# ✅ NSE 100 Stocks Universe (Optimized for Memory)
nse_100_stocks = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "LT", "ITC",
    "SBIN", "HINDUNILVR", "BHARTIARTL", "ASIANPAINT", "MARUTI", "SUNPHARMA", "HCLTECH",
    "WIPRO", "ULTRACEMCO", "NESTLEIND", "AXISBANK", "BAJFINANCE", "POWERGRID", "TITAN",
    "NTPC", "GRASIM", "ONGC", "TECHM", "JSWSTEEL", "TATAMOTORS", "HDFCLIFE", "INDUSINDBK",
    "BAJAJFINSV", "ADANIENT", "ADANIPORTS", "DIVISLAB", "COALINDIA", "CIPLA", "BRITANNIA",
    "BPCL", "HINDALCO", "EICHERMOT", "TATACONSUM", "DRREDDY", "HEROMOTOCO", "GAIL", "SBILIFE",
    "ICICIPRULI", "SHREECEM", "HAVELLS", "DLF", "AMBUJACEM", "SRF", "IOC", "PIDILITIND",
    "TATAPOWER", "BANKBARODA", "CHOLAFIN", "PEL", "BIOCON", "PNB", "AUROPHARMA", "BOSCHLTD",
    "LTI", "INDIGO", "SIEMENS", "BERGEPAINT", "TVSMOTOR", "VEDL", "NAUKRI", "DABUR", "COLPAL",
    "TORNTPHARM", "M&M", "BEL", "GODREJCP", "CROMPTON", "HDFCAMC", "IDFCFIRSTB", "UBL",
    "MUTHOOTFIN", "HINDPETRO", "LICHSGFIN", "CANBK", "INDIAMART", "NMDC", "ZYDUSLIFE", "APOLLOHOSP",
    "TRENT", "ACC", "LUPIN", "PAGEIND", "BANDHANBNK", "JUBLFOOD", "GRINDWELL", "IRCTC",
    "ABB", "GODREJPROP", "ESCORTS", "ALOKINDS", "SYNGENE", "CANFINHOME"
]

# ✅ Sniper Trade Engine

def generate_sniper_trades():
    sniper_trades = []
    today = datetime.date.today().strftime("%Y-%m-%d")

    for symbol in nse_100_stocks:
        try:
            cmp = fetch_cmp(symbol)
            if cmp is None:
                print(f"❌ Could not fetch CMP for {symbol}")
                continue

            trade = generate_trade_signal(symbol, cmp)
            if trade:
                trade_entry = {
                    "date": today,
                    "symbol": trade["symbol"],
                    "type": trade["type"],
                    "entry": trade["entry"],
                    "cmp": cmp,
                    "target": trade["target"],
                    "sl": trade["sl"],
                    "pop": trade["pop"],
                    "action": trade["action"],
                    "sector": trade.get("sector", "NSE 100 ✅"),
                    "tags": trade.get("tags", [])
                }
                sniper_trades.append(trade_entry)
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")

    # Save to trades.json
    with open("trades.json", "w") as f:
        json.dump(sniper_trades, f, indent=4)
    print(f"✅ {len(sniper_trades)} trades written to trades.json")
