from datetime import datetime
import random

def get_all_trades():
    today = datetime.today().strftime("%Y-%m-%d")

    # Simulated trades with logic tags (replace with live data later)
    trades = [
        {
            "date": today,
            "symbol": "CIPLA JUL FUT",
            "type": "Futures",
            "entry": 1520,
            "cmp": 1531.50,
            "target": 1548,
            "sl": 1502,
            "pop": "87%",
            "action": "Buy",
            "sector": "Pharma ✅",
            "tags": ["High PoP / Clean Structure", "VWAP Support", "MACD Crossover", "RSI > 55", "OBV Confirmed", "No Trap", "Heikin Ashi"]
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
            "tags": ["High PoP / Trap Risk", "RSI > 60", "OBV Divergence", "VWAP Tested", "Option Validated", "ICT Liquidity Grab"]
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
            "tags": ["1.5 SD Range", "IV Neutral", "High OI", "Consolidation Zone", "High PoP / Clean Structure", "VWAP Centered"]
        }
    ]

    return trades
