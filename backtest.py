#!/usr/bin/env python
"""
backtest.py

1) Authenticate Kite via env vars (KITE_API_KEY & KITE_ACCESS_TOKEN)
2) Inject Kite into utils
3) Loop through your parameter grid and symbols
4) Fetch OHLC & indicators via utils.fetch_*
5) Record results to results.json
"""

import os
import json
from datetime import date

from kiteconnect import KiteConnect

import utils
from utils import fetch_ohlc, fetch_rsi, fetch_adx, fetch_macd
from instruments import FNO_SYMBOLS

# ── 1) AUTHENTICATE via environment variables ──────────────────────────────
API_KEY      = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")
if not (API_KEY and ACCESS_TOKEN):
    raise RuntimeError("Both KITE_API_KEY and KITE_ACCESS_TOKEN must be set as secrets")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)
utils.set_kite(kite)

# ── 2) Define your parameter grid ──────────────────────────────────────────
# Example grid: (RSI_MIN, ADX_MIN, VOL_MULTIPLIER, DONCHIAN_WINDOW, SIGMA)
grid = [
    (rsi_min, adx_min, vol_mul, dc_win, sigma)
    for rsi_min in [45, 50, 55]
    for adx_min in [20, 25, 30]
    for vol_mul in [1.0, 1.5]
    for dc_win in [10, 20]
    for sigma in [1, 2]
]

# ── 3) Per‐symbol backtest logic ────────────────────────────────────────────
def run_symbol(sym, rsi_min, adx_min, vol_mul, dc_win, sigma):
    df = fetch_ohlc(sym, 800)   # ~3 years of daily bars
    if df is None or df.empty:
        return []

    results = []
    # --- Example logic: simple RSI+ADX filter ---
    for i in range(dc_win, len(df)):
        price = df["close"].iloc[i]
        if fetch_rsi(sym) is None or fetch_adx(sym) is None:
            continue
        if fetch_rsi(sym) >= rsi_min and fetch_adx(sym) >= adx_min:
            # simulate a buy at 'price'
            # placeholder: you can expand this to track SL, Target, P&L, etc.
            results.append({
                "symbol": sym,
                "date":    df.index[i].strftime("%Y-%m-%d") if hasattr(df.index[i], "strftime") else str(df.index[i]),
                "entry":   round(price, 2),
                "rsi":     round(fetch_rsi(sym), 2),
                "adx":     round(fetch_adx(sym), 2),
                "macd":    round(fetch_macd(sym) or 0.0, 2),
            })
    return results

# ── 4) Aggregate metrics per combo ─────────────────────────────────────────
def run_combo(rsi_min, adx_min, vol_mul, dc_win, sigma):
    all_trades = []
    for sym in FNO_SYMBOLS:
        trades = run_symbol(sym, rsi_min, adx_min, vol_mul, dc_win, sigma)
        all_trades.extend(trades)

    return {
        "RSI_MIN":        rsi_min,
        "ADX_MIN":        adx_min,
        "VOL_MULTIPLIER": vol_mul,
        "DONCHIAN_WINDOW": dc_win,
        "N_SIGMA_PRIMARY": sigma,
        "trade_count":    len(all_trades),
        # You can compute additional metrics here, e.g. win-rate, avg P&L, sharpe, etc.
    }

# ── 5) Execute grid and write results ───────────────────────────────────────
if __name__ == "__main__":
    results = []
    for combo in grid:
        res = run_combo(*combo)
        results.append(res)
        print(f"🔄 Completed combo {combo} → trades: {res['trade_count']}")

    # write out results.json for review
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Backtest complete; wrote {len(results)} parameter combos to results.json.")
