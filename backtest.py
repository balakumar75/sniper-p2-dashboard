#!/usr/bin/env python
"""
backtest.py

1) Authenticate Kite & inject into utils
2) Loop through parameter grid and symbols
3) Fetch OHLC & indicators via utils.fetch_*
4) Record P&L, win-rate, etc.
"""

import os
import json
from datetime import date

import kite_patch
from token_manager import refresh_if_needed

import utils
from utils import fetch_ohlc, fetch_rsi, fetch_adx, fetch_macd
from instruments import FNO_SYMBOLS

# ── 1) AUTHENTICATE & INJECT ────────────────────────────────────────────────
kite = refresh_if_needed()
utils.set_kite(kite)

# ── 2) YOUR GRID & RUNNER (unchanged) ───────────────────────────────────────

# example grid definition (RSI, ADX, VOL_MULTIPLIER, DONCHIAN_WINDOW, N_SIGMA_PRIMARY)
grid = [
    (rsi, adx, vol, dc, sigma)
    for rsi in [45, 50, 55]
    for adx in [20, 25, 30]
    for vol in [1.0, 1.5]
    for dc in [10, 20]
    for sigma in [1, 2]
]

def run_symbol(sym, rsi_min, adx_min, vol_mul, dc_win, sigma):
    df = fetch_ohlc(sym, 800)   # about 3 yrs
    if df is None: return []
    results = []
    # ... your existing backtest logic using fetch_rsi, fetch_adx, fetch_macd, etc.
    # e.g.:
    # for idx in range(dc_win, len(df)):
    #     price = df["close"].iloc[idx]
    #     if fetch_rsi(sym) >= rsi_min and fetch_adx(sym) >= adx_min:
    #         # simulate trade, compute pnl, append to results
    return results

def run_combo(rsi_min, adx_min, vol_mul, dc_win, sigma):
    all_trades = []
    for sym in FNO_SYMBOLS:
        trades = run_symbol(sym, rsi_min, adx_min, vol_mul, dc_win, sigma)
        all_trades.extend(trades)
    # compute aggregate metrics (win-rate, sharpe, etc.)
    return {
        "RSI": rsi_min,
        "ADX": adx_min,
        "VOL": vol_mul,
        "DC":  dc_win,
        "SIGMA": sigma,
        "trades": len(all_trades),
        # add your other metrics here
    }

if __name__ == "__main__":
    results = []
    for combo in grid:
        res = run_combo(*combo)
        results.append(res)
        print(f"Completed combo {combo}: {res}")

    # write out best_params.json and results.csv/backtest_report.md as before
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Backtest complete; results.json written.")
