import json
from utils import fetch_cmp, generate_trade_signal, get_kite_client

def generate_sniper_trades():
    kite = get_kite_client()  # ✅ Authenticate Zerodha session

    nse_100_stocks = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "LT", "ITC", "SBIN", "HINDUNILVR",
        "BHARTIARTL", "ASIANPAINT", "MARUTI", "SUNPHARMA", "HCLTECH", "WIPRO", "ULTRACEMCO", "NESTLEIND",
        "AXISBANK", "BAJFINANCE", "POWERGRID", "TITAN", "NTPC", "GRASIM", "ONGC", "TECHM", "JSWSTEEL",
        "TATAMOTORS", "HDFCLIFE", "INDUSINDBK", "BAJAJFINSV", "ADANIENT", "ADANIPORTS", "DIVISLAB", "COALINDIA",
        "CIPLA", "BRITANNIA", "BPCL", "HINDALCO", "EICHERMOT", "TATACONSUM", "DRREDDY", "HEROMOTOCO", "GAIL",
        "SBILIFE", "ICICIPRULI", "SHREECEM", "HAVELLS", "DLF", "AMBUJACEM", "SRF", "IOC", "PIDILITIND",
        "TATAPOWER", "BANKBARODA", "CHOLAFIN", "PEL", "BIOCON", "PNB", "AUROPHARMA", "BOSCHLTD", "LTI",
        "INDIGO", "SIEMENS", "BERGEPAINT", "TVSMOTOR", "VEDL", "NAUKRI", "DABUR", "COLPAL", "TORNTPHARM", "M&M",
        "BEL", "GODREJCP", "CROMPTON", "HDFCAMC", "IDFCFIRSTB", "UBL", "MUTHOOTFIN", "HINDPETRO", "LICHSGFIN",
        "CANBK", "INDIAMART", "NMDC", "ZYDUSLIFE", "APOLLOHOSP", "TRENT", "ACC", "LUPIN", "PAGEIND", "BANDHANBNK",
        "JUBLFOOD", "GRINDWELL", "IRCTC", "ABB", "GODREJPROP", "ESCORTS", "ALOKINDS", "SYNGENE", "CANFINHOME"
    ]

    all_trades = []

    for symbol in nse_100_stocks:
        try:
            cmp = fetch_cmp(kite, symbol)  # ✅ Fix: pass kite and symbol
            trade = generate_trade_signal(symbol, cmp)
            if trade:
                all_trades.append(trade)
        except Exception as e:
            print(f"❌ Error processi
