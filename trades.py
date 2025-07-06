from datetime import datetime

def get_all_trades():
    return [
        {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "symbol": "CIPLA JUL FUT",
            "type": "Futures",
            "entry": 1520,
            "cmp": 1531.5,
            "target": 1548,
            "sl": 1502,
            "pop": "87%",
            "action": "Buy",
            "sector": "Pharma ✅",
            "tags": ["RSI > 55", "VWAP Support", "OBV Confirmed"]
        }
    ]
