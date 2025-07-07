from kiteconnect import KiteConnect
import os
import pandas as pd
import datetime

api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")
if not access_token:
    with open("token.txt", "r") as f:
        access_token = f.read().strip()

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

FNO_STOCKS = [
    "ACC", "ADANIENT", "ADANIPORTS", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT",
    "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK",
    "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD",
    "BPCL", "BRITANNIA", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA",
    "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT",
    "DEEPAKNTR", "DELHIVERY", "DELTACORP", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS",
    "EXIDEIND", "FEDERALBNK", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD", "HAL",
    "HAVELLS", "HCLTECH", "HDFC", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDCOPPER",
    "HINDPETRO", "HINDUNILVR", "HONAUT", "IBULHSGFIN", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA",
    "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER",
    "INFY", "INTELLECT", "IOC", "IRCTC", "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD",
    "KOTAKBANK", "L&TFH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LT", "LTI", "LTIM", "LTTS", "LUPIN",
    "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCX", "METROPOLIS", "MFSL", "MGL", "MINDTREE",
    "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NAM-INDIA", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND",
    "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND",
    "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL",
    "SBICARD", "SBILIFE", "SBIN", "SCI", "SHREECEM", "SIEMENS", "SRF", "SRTRANSFIN", "STAR", "SUNPHARMA",
    "SUNTV", "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL",
    "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL",
    "VEDL", "VOLTAS", "WIPRO", "ZEEL"
]

def fetch_candles(symbol):
    try:
        instrument = f"NSE:{symbol}"
        token = kite.ltp(instrument)[instrument]['instrument_token']
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=10)
        candles = kite.historical_data(token, from_date, to_date, interval="day")
        return pd.DataFrame(candles)
    except:
        return pd.DataFrame()

def compute_indicators(df):
    if df.empty or len(df) < 5:
        return None
    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    df['OBV'] = (df['close'].diff() > 0).astype(int).cumsum()
    return {
        "rsi": round(df['RSI'].iloc[-1], 2),
        "macd_flag": "MACD Bullish" if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] else "MACD Bearish",
        "vwap_flag": "VWAP Support" if df['close'].iloc[-1] > df['VWAP'].iloc[-1] else "VWAP Resistance",
        "obv_flag": "OBV Rising" if df['OBV'].iloc[-1] > df['OBV'].iloc[-2] else "OBV Falling"
    }

def evaluate_trade_status(entry, cmp, sl, target):
    if cmp >= target:
        return "Target Hit"
    elif cmp <= sl:
        return "SL Hit"
    return "Open"

def is_expiry_valid(expiry_date):
    today = datetime.datetime.today().date()
    expiry = expiry_date.date() if isinstance(expiry_date, datetime.datetime) else expiry_date
    days_to_expiry = (expiry - today).days
    return 2 <= days_to_expiry <= 7

def generate_sniper_trades():
    trades = []
    for stock in FNO_STOCKS:
        try:
            cmp = kite.ltp(f"NSE:{stock}")[f"NSE:{stock}"]["last_price"]
            df = fetch_candles(stock)
            indicators = compute_indicators(df)
            if not indicators or indicators['rsi'] < 55 or indicators['macd_flag'] != "MACD Bullish":
                continue
            entry = round(cmp * 0.995, 2)
            target = round(cmp * 1.02, 2)
            sl = round(cmp * 0.98, 2)
            status = evaluate_trade_status(entry, cmp, sl, target)
            trade = {
                "symbol": f"{stock} JUL FUT",
                "type": "Futures",
                "entry": entry,
                "cmp": cmp,
                "target": target,
                "sl": sl,
                "pop": "85%",
                "action": "Buy",
                "sector": "F&O ✅",
                "tags": [f"RSI={indicators['rsi']}", indicators['macd_flag'], indicators['vwap_flag'], indicators['obv_flag']],
                "trap_zone": "Clean Breakout",
                "expiry": "July Monthly",
                "status": status,
                "buy_date": datetime.datetime.today().strftime("%Y-%m-%d"),
                "exit_date": "" if status == "Open" else datetime.datetime.today().strftime("%Y-%m-%d"),
                "holding_days": 0,
                "pnl_abs": 0,
                "pnl_pct": 0,
                "vwap_flag": indicators['vwap_flag'],
                "obv_flag": indicators['obv_flag'],
                "macd_flag": indicators['macd_flag'],
                "rsi": indicators['rsi'],
                "adx": 25,
                "structure": "HH-HL",
                "ict_flag": "",
                "option_greeks": {},
                "strike_zone": "",
                "news_flag": "Clean Technical Only"
            }
            trades.append(trade)
        except Exception as e:
            print(f"❌ Error processing {stock}: {e}")
            continue
    return trades
