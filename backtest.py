"""
backtest.py  –  Eval grid of parameter sets over 3-year history
Outputs: results.csv and backtest_report.md
"""

import itertools, json, pathlib, datetime as dt, pandas as pd
from tqdm import tqdm
from config import DEFAULT_POP, NSE100    # reuse constants
from utils  import (fetch_ohlc, fetch_rsi, fetch_adx, fetch_macd)

START = dt.date.today() - dt.timedelta(days=3*365)

# ── parameter grid ─────────────────────────────────────────────────────
GRID = {
    "RSI_MIN":        [45, 50, 55],
    "ADX_MIN":        [15, 18, 20],
    "VOL_MULT":       [1.0, 1.2, 1.5],
    "DONCHIAN_WIN":   [20, 30],
    "SIGMA":          [1.0, 1.25]
}
COMBOS = list(itertools.product(*GRID.values()))

# ── simple P&L calc (cash leg only) ────────────────────────────────────
def trade_pnl(entry, exit):
    return (exit - entry) / entry

def run_combo(rsi_min, adx_min, vol_mult, dc_win, sigma):
    records = []
    for sym in NSE100:                        # assume NSE100 list in config
        df = fetch_ohlc(sym, 800)             # 2+ yrs data
        if df is None or df.empty: continue
        df = df[df["date"] >= pd.Timestamp(START)]
        high = df["high"].rolling(dc_win).max()
        low  = df["low"].rolling(dc_win).min()
        for i in range(dc_win, len(df)):
            price = df["close"].iat[i]
            if (price >= high.iat[i] and
                fetch_rsi(sym) >= rsi_min and
                fetch_adx(sym) >= adx_min and
                fetch_macd(sym) and
                df["volume"].iat[i] > vol_mult * df["volume"].iloc[i-dc_win:i].mean()):
                entry = price
                exit_ = df["close"].iat[min(i+5, len(df)-1)]   # 5-day hold
                records.append(trade_pnl(entry, exit_))
    if not records:
        return None
    pnl_series = pd.Series(records)
    cagr = (1 + pnl_series.mean()) ** (252/5) - 1   # 5-day hold
    return dict(
        RSI=rsi_min, ADX=adx_min, VOL=vol_mult,
        DC=dc_win, SIGMA=sigma,
        trades=len(records),
        winrate=(pnl_series>0).mean(),
        avgPnl=pnl_series.mean(),
        sharpe=pnl_series.mean()/pnl_series.std(),
        CAGR=cagr
    )

# ── run grid ───────────────────────────────────────────────────────────
out = []
for combo in tqdm(COMBOS, desc="grid"):
    res = run_combo(*combo)
    if res: out.append(res)

pd.DataFrame(out).to_csv("results.csv", index=False)

best = max(out, key=lambda r: (r["CAGR"], r["sharpe"]))
pathlib.Path("best_params.json").write_text(json.dumps(best, indent=2))
