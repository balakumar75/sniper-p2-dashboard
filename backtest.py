"""
backtest.py – grid-search tuner (3-year back-test)

Adds:
  • 0.35 s sleep between every OHLC fetch  → stays inside Zerodha 3 req/s limit
  • safe exit when no results
"""

import itertools, json, pathlib, datetime as dt, time
import pandas as pd
from tqdm import tqdm
from config import NSE100, DEFAULT_POP
from utils  import fetch_ohlc, fetch_rsi, fetch_adx, fetch_macd

START = dt.date.today() - dt.timedelta(days=3*365)

# ── parameter grid ──────────────────────────────────────────────────────
GRID = {
    "RSI_MIN":      [45, 50, 55],
    "ADX_MIN":      [15, 18, 20],
    "VOL_MULT":     [1.0, 1.2, 1.5],
    "DC_WIN":       [20, 30],
    "SIGMA":        [1.0, 1.25],
}
COMBOS = list(itertools.product(*GRID.values()))

# ── simple cash-only P&L helper ─────────────────────────────────────────
def trade_pnl(entry, exit_):
    return (exit_ - entry) / entry

# ── run one combo on one symbol ─────────────────────────────────────────
def run_symbol(sym, rsi_min, adx_min, vol_mult, dc_win):
    df = fetch_ohlc(sym, 800)   # about 3 yrs of dailies
    time.sleep(0.35)            # throttle → 3 req/s
    if df is None or df.empty:
        return []

    df = df[df["date"] >= pd.Timestamp(START)]
    high = df["high"].rolling(dc_win).max()
    low  = df["low"].rolling(dc_win).min()
    trades = []

    for i in range(dc_win, len(df)):
        price = df["close"].iat[i]
        if (price >= high.iat[i] and
            fetch_rsi(sym) >= rsi_min and
            fetch_adx(sym) >= adx_min and
            fetch_macd(sym) and
            df["volume"].iat[i] >
            vol_mult * df["volume"].iloc[i-dc_win:i].mean()):

            entry = price
            exit_ = df["close"].iat[min(i+5, len(df)-1)]  # 5-day hold
            trades.append(trade_pnl(entry, exit_))
    return trades

# ── run full combo over NSE100 ──────────────────────────────────────────
def run_combo(rsi, adx, vol, dc, sigma):
    all_trades = []
    for sym in NSE100:
        all_trades.extend(run_symbol(sym, rsi, adx, vol, dc))

    if not all_trades:
        return None

    s = pd.Series(all_trades)
    annual_factor = 252/5                     # 5-day avg hold
    cagr   = (1 + s.mean())**annual_factor - 1
    sharpe = s.mean()/s.std()

    return dict(RSI=rsi, ADX=adx, VOL=vol, DC=dc, SIGMA=sigma,
                trades=len(s), winrate=(s>0).mean(),
                avgPnl=s.mean(), sharpe=sharpe, CAGR=cagr)

# ── grid sweep ──────────────────────────────────────────────────────────
results = []
for combo in tqdm(COMBOS, desc="grid"):
    res = run_combo(*combo)
    if res:
        results.append(res)

# ── handle empty result set gracefully ──────────────────────────────────
if not results:
    print("❌ All OHLC fetches failed (rate-limit?) – no tuning this run.")
    pathlib.Path("backtest_report.md").write_text(
        "# Weekly Back-test\n\n_No results – likely due to API rate-limit._\n")
    exit(0)

pd.DataFrame(results).to_csv("results.csv", index=False)

best = max(results, key=lambda r: (r["CAGR"], r["sharpe"]))
pathlib.Path("best_params.json").write_text(json.dumps(best, indent=2))
print("✅ Best combo:", best)
