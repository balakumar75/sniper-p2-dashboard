"""
sniper_engine.py  •  Multi-factor Scoring Sniper Engine
"""
from typing import List, Dict
from datetime import date
import os, math

from instruments import FNO_SYMBOLS
import utils

# ── CONFIG ─────────────────────────────────────────────────────────────────
TREND_N    = 200
ADX_N      = 14
ATR_N      = 14
SL_PCT     = 2.0
TGT_PCT    = 3.0
RISK_PCT   = 0.01    # 1% risk per trade

# Weights must sum to 1
WEIGHTS = {
    "trend": 0.30,
    "adx":   0.15,
    "vol":   0.10,
    "liq":   0.10,
    "rsi":   0.20,
    "pop":   0.15,
}
SCORE_THRESHOLD = 0.65

# Read account size from env or default ₹1 Crore
ACCOUNT_SIZE = float(os.getenv("ACCOUNT_SIZE", "10000000"))

# ── helper to normalize into [0,1] ─────────────────────────────────────────
def normalize(val, low, high):
    return max(0.0, min(1.0, (val - low) / (high - low)))

# ── MAIN scanner ────────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    ideas = []

    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 260)
        if df is None or df.empty:
            continue

        close = df["close"]
        # 1) Trend filter & norm
        sma200      = utils.sma(close, TREND_N).iloc[-1]
        trend_norm  = 1.0 if close.iloc[-1] > sma200 else 0.0

        # 2) ADX norm (0–50)
        adx_val     = utils.adx(df, ADX_N).iloc[-1]
        adx_norm    = normalize(adx_val, 0, 50)

        # 3) ATR% norm (1–3%)
        atr_val     = utils.atr(df, ATR_N).iloc[-1]
        atr_pct     = atr_val / close.iloc[-1]
        vol_norm    = normalize(atr_pct, 0.01, 0.03)

        # 4) Liquidity norm (0–₹100Cr)
        liq_cr      = utils.avg_turnover(df, 20)
        liq_norm    = normalize(liq_cr, 0, 100)

        # 5) RSI norm (40–80)
        rsi_val     = utils.rsi(df, 14).iloc[-1]
        rsi_norm    = normalize(rsi_val, 40, 80)

        # 6) Historical PoP
        pop_val     = utils.hist_pop(df, TGT_PCT, SL_PCT, lookback=90) or 0.0

        # 7) Composite score
        score = (
            WEIGHTS["trend"] * trend_norm +
            WEIGHTS["adx"]   * adx_norm   +
            WEIGHTS["vol"]   * vol_norm   +
            WEIGHTS["liq"]   * liq_norm   +
            WEIGHTS["rsi"]   * rsi_norm   +
            WEIGHTS["pop"]   * pop_val
        )

        if score < SCORE_THRESHOLD:
            continue

        entry       = close.iloc[-1]
        stop_price  = entry * (1 - SL_PCT/100)
        dollar_risk = entry - stop_price
        qty = int((ACCOUNT_SIZE * RISK_PCT) / dollar_risk) if dollar_risk > 0 else 0

        ideas.append({
            "date":    today,
            "symbol":  sym,
            "entry":   round(entry, 2),
            "cmp":     round(entry, 2),
            "target":  round(entry * (1 + TGT_PCT/100), 2),
            "sl":      round(stop_price, 2),
            "pop":     round(pop_val, 2),
            "score":   round(score, 2),
            "qty":     qty,
            "pnl":     0.0,
            "action":  "Buy",
        })

    return ideas
