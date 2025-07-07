from kiteconnect import KiteConnect
import os
from sniper_engine.utils import get_rsi, get_macd, get_obv, get_adx, get_vwap, calculate_pop

# Initialize KiteConnect using your API key and token from environment variables
kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
kite.set_access_token(os.getenv("KITE_ACCESS_TOKEN"))

def generate_sniper_trades():
    fno_symbols = [
        "CIPLA", "BEL", "HDFCBANK", "LTIM", "RELIANCE", "ICICIBANK", "SBIN", "TCS"
    ]
    trades = []

    for symbol in fno_symbols:
        try:
            instrument = f"NSE:{symbol}"
            ltp_data = kite.ltp(instrument)
            cmp = ltp_data[instrument]['last_price']

            # Calculate indicators
            rsi = get_rsi(symbol)
            macd = get_macd(symbol)
            obv = get_obv(symbol)
            adx = get_adx(symbol)
            vwap = get_vwap(symbol)

            # Strategy conditions
            if rsi > 55 and macd["signal"] == "bullish" and obv == "up" and adx > 20 and cmp > vwap:
                entry = round(cmp)
                sl = round(entry * 0.98)
                target = round(entry * 1.025)
                pop = calculate_pop(rsi, macd, adx, obv)

                trade = {
                    "date": "2025-07-08",
                    "symbol": f"{symbol} JUL FUT",
                    "type": "Futures",
                    "entry": entry,
                    "cmp": cmp,
                    "target": target,
                    "sl": sl,
                    "pop": f"{pop}%",
                    "action": "Buy",
                    "sector": "To be tagged",
                    "tags": [
                        "RSI Buy âœ…",
                        "MACD âœ…" if macd["signal"] == "bullish" else "MACD âŒ",
                        "OBV Up âœ…" if obv == "up" else "OBV âŒ",
                        "VWAP Hold âœ…" if cmp > vwap else "VWAP âŒ"
                    ],
                    "status": "Open"
                }

                trades.append(trade)
        except Exception as e:
            print(f"âš ï¸ Error processing {symbol}: {e}")

    return trades
