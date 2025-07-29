#!/usr/bin/env python
import json, pathlib, os
from datetime import date

import kite_patch
from token_manager import refresh_if_needed
import utils

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Load open trades from docs
docs_file = pathlib.Path("docs/trades.json")
open_trades = json.loads(docs_file.read_text()) if docs_file.exists() else []

today = date.today().isoformat()
still_open, just_closed = [], []

# 3) Check each
for t in open_trades:
    # fetch latest close
    df = utils.fetch_ohlc(t["symbol"], days=1)
    if df is None or df.empty:
        still_open.append(t)
        continue
    price = float(df["close"].iloc[-1])

    if t.get("target") is not None and price >= t["target"]:
        t["status"]    = "Target Hit"
        t["exit_date"] = today
        just_closed.append(t)
    elif t.get("sl") is not None and price <= t["sl"]:
        t["status"]    = "SL Hit"
        t["exit_date"] = today
        just_closed.append(t)
    else:
        t["cmp"] = price
        still_open.append(t)

# 4) Write back open
docs_file.write_text(json.dumps(still_open, indent=2))

# 5) Append closed to history
hist_file = pathlib.Path("trade_history.json")
history = json.loads(hist_file.read_text()) if hist_file.exists() else []
history.extend(just_closed)
hist_file.write_text(json.dumps(history, indent=2))

# 6) Commit & push
os.system('git config user.name "monitor-bot"')
os.system('git config user.email "bot@users.noreply.github.com"')
os.system('git add docs/trades.json trade_history.json')
os.system('git commit -m "Update trade statuses '+today+'" || echo "No changes"')
os.system('git push origin main')
