import json
from utils import fetch_cmp, generate_trade_signal

def generate_sniper_trades():
    symbols = [
        "CIPLA", "SUNPHARMA", "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "INFY", "TCS", "WIPRO", "ITC",
        "HINDUNILVR", "LT", "POWERGRID", "NTPC", "ASIANPAINT", "BAJFINANCE", "AXISBANK", "KOTAKBANK", "TITAN",
        "EICHERMOT", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "ADANIENT", "ADANIPORTS", "DRREDDY", "COLPAL", "BEL",
        "HAL", "DLF", "DIVISLAB", "INDUSINDBK", "TECHM", "HCLTECH", "UPL", "GRASIM", "ULTRACEMCO", "BHARTIARTL",
        "MARUTI", "BAJAJ_AUTO", "HEROMOTOCO", "BPCL", "IOC", "HINDALCO", "VEDL", "COALINDIA", "M&M", "AMBUJACEM",
        "SBILIFE", "ICICIGI", "ICICIPRULI", "TATACONSUM", "BRITANNIA", "DABUR", "GODREJCP", "PIDILITIND", "SHREECEM",
        "NAUKRI", "HAVELLS", "BAJAJFINSV", "CHOLAFIN", "MUTHOOTFIN", "PEL", "SRF", "TORNTPHARM", "APOLLOHOSP",
        "GLAND", "CROMPTON", "BOSCHLTD", "TRENT", "ZOMATO", "DMART", "IRCTC", "MCX", "IEX", "GUJGASLTD", "ZEEL",
        "IDFCFIRSTB", "INDIAMART", "BANDHANBNK", "TATAPOWER", "PFC", "ONGC", "JSPL", "CONCOR", "ABB", "PAGEIND"
    ]

    trades = []
    failed = []

    for symbol in symbols:
        print(f"🔍 Fetching CMP for: {symbol}")
        cmp = fetch_cmp(symbol)

        if cmp:
            print(f"✅ CMP for {symbol}: {cmp}")
            trade = generate_trade_signal(symbol, cmp)
            if trade:
                trades.append(trade)
        else:
            print(f"❌ Failed to fetch CMP for: {symbol}")
            failed.append(symbol)

    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)

    print(f"\n✅ {len(trades)} sniper trades generated.")
    if failed:
        print(f"⚠️ {len(failed)} symbols failed CMP fetch:")
        for s in failed:
            print(" -", s)

def save_trades_to_json(trades):
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)

if __name__ == "__main__":
    generate_sniper_trades()
