"""
sniper_learn.py – ultra-simple rule-based tuner
Run DAILY after market close (e.g. 16:20 IST).

Logic:
• Look at past trades in performance.json
• If SL-rate > 60 % when ADX<25 → raise ADX_MIN by +2
Writes new values to sniper_params.json so next engine run auto-uses them.
"""

import json, pathlib, datetime

PERF   = pathlib.Path("performance.json")
PARAMS = pathlib.Path("sniper_params.json")

records = json.loads(PERF.read_text()) if PERF.exists() else []
if not records:
    print("No performance data yet – nothing to tune.")
    raise SystemExit(0)

# Filter trades where ADX < 25
adx_trades   = [r for r in records if r.get("adx", 0) < 25]
adx_sl_hits  = [r for r in adx_trades if r["result"] == "SL"]

if adx_trades and len(adx_sl_hits) / len(adx_trades) > 0.60:
    new_params = {"RSI_MIN": 55, "ADX_MIN": 22, "VOL_MULTIPLIER": 1.5}
    PARAMS.write_text(json.dumps(new_params, indent=2))
    print("🔧 Raised ADX_MIN to 22 based on recent SL hits.")
else:
    print("No parameter change today.")
