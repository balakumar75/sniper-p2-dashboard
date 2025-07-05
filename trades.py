from datetime import datetime

def get_all_trades():
    return [
        {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "symbol": "CIPLA JUL FUT",
            "type": "Futures",
            "entry": 1520,
            "cmp": 1532.10,
            "target": 1548,
            "sl": 1502,
            "pop": "87%",
            "action": "Buy",
            "sector": "Pharma ✅",
            "tags": ["Clean Breakout", "High PoP", "Confirmed Structure"]
        },
        {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "symbol": "RELIANCE 2940 CE",
            "type": "Options (Weekly)",
            "entry": 42,
            "cmp": 49.5,
            "target": 58,
            "sl": 36,
            "pop": "82%",
            "action": "Buy",
            "sector": "Energy ✅",
            "tags": ["OBV Surge", "MACD Cross", "High Volume"]
        }
    ]
