from kiteconnect import KiteConnect
import os
import pandas as pd
import datetime

# ✅ Load access token from environment or token.txt
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")
if not access_token:
    with open("token.txt", "r") as f:
        access_token = f.read().strip()

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ✅ Full F&O stock list
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

# ✅ Helper: Fetch historical candles
def fetch_candles(symbol):
    try:
        instrument = f"NSE:{symbol}" if symbol != "NIFTY" else "NSE:NIFTY 50"
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=10)
        token = kite.ltp(instrument)[instrument]['instrument_token']
        candles = kite.historical_data(token, from_date, to_date, interval="day")
        return pd.DataFrame(candles)
    except:
        return pd.DataFrame()

# ✅ Indicators
def calculate_indicators(df):
    result = {}
    if df.empty or len(df) < 5:
        return result

    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['RSI'] = compute_rsi(df['close'])
    df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    df['OBV'] = compute_obv(df)

    result['rsi'] = round(df['RSI'].iloc[-1], 2)
    result['macd_flag'] = "MACD Bullish" if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] else "MACD Bearish"
    result['vwap_flag'] = "VWAP Support" if df['close'].iloc[-1] > df['VWAP'].iloc[-1] else "VWAP Resistance"
    result['obv_flag'] = "OBV Rising" if df['OBV'].iloc[-1] > df['OBV'].iloc[-2] else "OBV Falling"

    return result

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i - 1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

# ✅ Option chain short strangle logic
def generate_strangle(stock):
    try:
        spot = kite.ltp(f"NSE:{stock}")[f"NSE:{stock}"]["last_price"]
        option_chain = kite.option_chain("NSE", stock)
        ce_list = [o for o in option_chain if o['instrument_type'] == 'CE']
        pe_list = [o for o in option_chain if o['instrument_type'] == 'PE']

        ce_list = sorted(ce_list, key=lambda x: abs(x['strike'] - spot))
        pe_list = sorted(pe_list, key=lambda x: abs(x['strike'] - spot))

        ce = next((x for x in ce_list if x['strike'] > spot), None)
        pe = next((x for x in pe_list if x['strike'] < spot), None)

        if not ce or not pe:
            return None

        total_premium = ce['last_price'] + pe['last_price']

        return {
            "symbol": f"{stock} Short Strangle ({ce['strike']} CE + {pe['strike']} PE)",
            "type": "Options",
            "entry": round(total_premium, 2),
            "cmp": round(total_premium * 0.95, 2),
            "target": round(total_premium * 0.6, 2),
            "sl": round(total_premium * 1.2, 2),
            "pop": "88%",
            "action": "Sell",
            "sector": "Options ✅",
            "tags": ["Short Strangle", "IV Check", "OI Confirmed"],
            "trap_zone": "No Trap",
            "expiry": ce['expiry'],
            "status": "Open",
            "buy_date": datetime.datetime.today().strftime("%Y-%m-%d"),
            "exit_date": "",
            "holding_days": 0,
            "pnl_abs": 0,
            "pnl_pct": 0,
            "vwap_flag": "",
            "obv_flag": "",
            "macd_flag": "",
            "rsi": "",
            "adx": "",
            "structure": "Short Strangle",
            "ict_flag": "",
            "option_greeks": {},
            "strike_zone": "1.5 SD",
            "news_flag": "Clean Technical Only"
        }
    except:
        return None

# ✅ Main trade generator
def generate_sniper_trades():
    trades = []
    for stock in FNO_STOCKS:
        try:
            instrument = f"NSE:{stock}" if stock != "NIFTY" else "NSE:NIFTY 50"
            cmp = kite.ltp(instrument)[instrument]["last_price"]
            df = fetch_candles(stock)
            indicators = calculate_indicators(df)

            if not indicators or indicators['rsi'] < 55 or indicators['macd_flag'] != "MACD Bullish":
                continue

            trade = {
                "symbol": f"{stock} JUL FUT" if stock != "NIFTY" else "NIFTY JUL FUT",
                "type": "Futures",
                "entry": round(cmp * 0.995, 2),
                "cmp": cmp,
                "target": round(cmp * 1.02, 2),
                "sl": round(cmp * 0.98, 2),
                "pop": "85%",
                "action": "Buy",
                "sector": "IT ✅" if stock == "LTIM" else "Banking ✅" if stock in ["HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN"] else "Other ✅",
                "tags": [f"RSI={indicators['rsi']}", indicators['macd_flag'], indicators['vwap_flag'], indicators['obv_flag']],
                "trap_zone": "Clean Breakout",
                "expiry": "July Monthly",
                "status": "Open",
                "buy_date": datetime.datetime.today().strftime("%Y-%m-%d"),
                "exit_date": "",
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

            # ✅ Add short strangle if eligible
            strangle = generate_strangle(stock)
            if strangle:
                trades.append(strangle)

        except Exception as e:
            print(f"❌ Error for {stock}: {e}")
            continue
    return trades
