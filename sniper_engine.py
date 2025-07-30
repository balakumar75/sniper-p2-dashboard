# sniper_engine.py

import os
import json
import math
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd

import utils
from config import FNO_SYMBOLS, RSI_MIN, ADX_MIN, VOL_MULTIPLIER, DEFAULT_POP

# ── 0) Try loading ML model (if it exists) ────────────────────────────────
try:
    artifact = joblib.load("model.pkl")
    MODEL    = artifact["model"]
    THRESH   = artifact.get("threshold", 0.5)
    print("✅ Loaded ML model from model.pkl")
except Exception:
    MODEL = None
    THRESH = None
    print("⚠️  model.pkl not found or failed to load — running rule‑based only")


# ── 1) Helpers ─────────────────────────────────────────────────────────────

def _rule_based_pop(df, tgt_pct, sl_pct):
    """Historic PoP fallback if no model."""
    return utils.hist_pop(df.name, tgt_pct, sl_pct)

def _ml_score(sym, entry, tgt_pct, sl_pct):
    """
    If MODEL is loaded, compute feature vector and return
    prediction probability for a win.
    """
    if MODEL is None: 
        return None
    rsi = utils.fetch_rsi(sym, period=14)
    adx = utils.fetch_adx(sym, period=14)
    atr = utils.fetch_atr(sym, period=14)
    vol = int(utils.fetch_ohlc(sym, 30)["volume"].iloc[-1] or 0)
    pop = utils.hist_pop(sym, tgt_pct, sl_pct)
    X   = np.array([[rsi, adx, atr, vol, pop]])
    return float(MODEL.predict_proba(X)[0,1])


# ── 2) Main engine ────────────────────────────────────────────────────────

def generate_sniper_trades():
    today = date.today().isoformat()
    trades = []

    for sym in FNO_SYMBOLS:
        # 1) Fetch daily candles
        df = utils.fetch_ohlc(sym, days=60)
        if df.empty: 
            continue

        # 2) Filter by momentum: RSI above threshold
        rsi = utils.fetch_rsi(sym, period=14)
        if rsi < RSI_MIN: 
            continue

        # 3) Trend strength via ADX
        adx = utils.fetch_adx(sym, period=14)
        if adx < ADX_MIN: 
            continue

        # 4) Calculate entry / SL / target
        last = df["close"].iloc[-1]
        atr  = utils.fetch_atr(sym, period=14)
        entry = round(last, 2)
        sl    = round(last - atr * VOL_MULTIPLIER, 2)
        tgt   = round(last + atr * VOL_MULTIPLIER, 2)

        # 5) Compute PoP: ML if available, else rule‑based
        tgt_pct = (tgt - entry) / entry * 100
        sl_pct  = (entry - sl) / entry * 100
        pop_ml  = _ml_score(sym, entry, tgt_pct, sl_pct)
        pop_rb  = utils.hist_pop(sym, tgt_pct, sl_pct)
        pop      = pop_ml if pop_ml is not None else pop_rb

        # 6) If ML, filter by threshold
        if MODEL is not None and pop < THRESH * 100:
            # skip low‑prob ML signals
            continue

        trades.append({
            "date":   today,
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  entry,
            "cmp":    entry,
            "target": tgt,
            "sl":     sl,
            "pop":    round(pop, 2),
            "status": "Open",
            "pnl":    0.0,
            "action": "Buy"
        })

    return trades


# ── 3) JSON dump helper ────────────────────────────────────────────────────

def save_trades_to_json(trades, path="trades.json"):
    with open(path, "w") as f:
        json.dump(trades, f, indent=2)

