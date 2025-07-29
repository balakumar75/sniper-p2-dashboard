#!/usr/bin/env python
import os, json, pathlib, requests
from datetime import date
import utils, ict_signals

# 1) Load open trades
docs_file = pathlib.Path("docs/trades.json")
trades = json.loads(docs_file.read_text()) if docs_file.exists() else []

# 2) Discord webhook URL (set in your secrets)
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
if not WEBHOOK:
    print("⚠️ No Discord webhook URL set.")
    exit(0)

today = date.today().isoformat()
alerts = []

for t in trades:
    sym = t["symbol"]
    # fetch current price
    df = utils.fetch_ohlc(sym, days=1)
    if not df: continue
    price = float(df["close"].iloc[-1])

    # check FVG
    gaps = ict_signals.detect_fvg(sym, lookback=5)
    for hi, lo in gaps:
        if lo < price < hi:
            alerts.append(f"🔔 {sym}: price {price} entered FVG [{lo:.2f}-{hi:.2f}]")

    # check Order‑Blocks
    obs = ict_signals.detect_order_blocks(sym, lookback=10)
    for hi, lo in obs:
        if lo < price < hi:
            alerts.append(f"🔔 {sym}: price {price} entered Order‑Block [{lo:.2f}-{hi:.2f}]")

# 3) send alerts
if alerts:
    payload = {"content": f"**Trade Alerts {today}**\n" + "\n".join(alerts)}
    r = requests.post(WEBHOOK, json=payload)
    print("✅ Sent", len(alerts), "alerts" if r.ok else "❌ failed")
