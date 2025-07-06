from datetime import datetime

def get_all_trades():
    today = datetime.today().strftime("%Y-%m-%d")

    trades = [
        {
            "date": today,
            "symbol": "CIPLA JUL FUT",
            "type": "Futures",
            "entry": 1520,
            "cmp": 1531.5,
            "target": 1548,
            "sl": 1502,
            "pop": "87%",
            "action": "Buy",
            "sector": "Pharma ✅",
            "tags": ["RSI > 55", "MACD Bullish", "VWAP Support", "OBV Confirmed", "Clean Structure", "Heikin Ashi ✅"]
        },
        {
            "date": today,
            "symbol": "RELIANCE 2940 CE (Weekly)",
            "type": "Options (Buy)",
            "entry": 42,
            "cmp": 49.5,
            "target": 58,
            "sl": 36,
            "pop": "82%",
            "action": "Buy",
            "sector": "Energy ✅",
            "tags": ["MACD Cross", "OBV Divergence", "VWAP Retest", "ICT Liquidity Grab", "Trap Risk ⚠️"]
        },
        {
            "date": today,
            "symbol": "HDFC BANK 1620 CE + 1540 PE (Monthly)",
            "type": "Short Strangle",
            "entry": 38.5,
            "cmp": 34.2,
            "target": 20,
            "sl": 48,
            "pop": "89%",
            "action": "Sell",
            "sector": "Banking ✅",
            "tags": ["1.5 SD Range", "IV Stable", "High OI", "Consolidation Zone", "VWAP Centered", "High PoP ✅"]
        }
    ]

    return trades
