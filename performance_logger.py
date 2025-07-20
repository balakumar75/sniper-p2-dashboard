"""
performance_logger.py – append a trade result when it closes.
Call log_result(trade_dict) whenever you mark status = "SL" or "Target".
"""

import json, pathlib, datetime

PERF = pathlib.Path("performance.json")

def log_result(trade: dict):
    trade_copy = trade.copy()
    trade_copy["timestamp"] = datetime.datetime.now().isoformat(timespec="seconds")
    data = json.loads(PERF.read_text()) if PERF.exists() else []
    data.append(trade_copy)
    PERF.write_text(json.dumps(data, indent=2))
