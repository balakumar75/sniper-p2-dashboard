# sniper_engine.py

import json
import math
from datetime import date

import joblib
import numpy as np

import utils
from config import FNO_SYMBOLS, RSI_MIN, ADX_MIN, VOL_MULTIPLIER

# Try load ML model (optional)
try:
    artifact = joblib.load("model.pkl")
    MODEL    = artifact["model"]
    THRESH   = artifact.get("threshold", 0.5)
    print("✅ Loaded ML model")
except Exception:
    MODEL = None
    THRESH = None
    print("⚠️  ML model not found — using rule‑based only")

def _compute_pop(sym, entry, tgt, sl):
    tgt_pct = (tgt - entry) / entry * 100
    sl_pct  = (entry - sl)    / entry * 100

    if MODEL:
        # ML probability
        score = MODEL.predict_proba([[ 
            utils.fetch_rsi(sym,14),
            utils.fetch_adx(sym,14),
            utils.fetch_atr(sym,14),
            int(utils.fetch_ohlc(sym,30)["volume"].iloc[-1] or 0),
            utils.hist_pop(sym, tgt_pct, sl_pct)
        ]])[0,1] * 100
        return round(score,2)
    else:
        # historical Pop
        return round(utils.hist_pop(sym, tgt_pct, sl_pct), 2)

def generate_sniper_trades():
    today = date.today().isoformat()
    trades = []

    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=60)
        if df.empty: 
            continue

        rsi = utils.fetch_rsi(sym,14)
        if rsi < RSI_MIN: 
            continue

        adx = utils.fetch_adx(sym,14)
        if adx < ADX_MIN:
            continue

        last = df["close"].iloc[-1]
        atr  = utils.fetch_atr(sym,14)
        entry = round(last,2)
        sl    = round(last - atr*VOL_MULTIPLIER,2)
        tgt   = round(last + atr*VOL_MULTIPLIER,2)

        pop = _compute_pop(sym, entry, tgt, sl)
        if MODEL and pop < THRESH*100:
            continue

        trades.append({
            "entry_date": today,
            "exit_date":  "",             # empty until closed
            "symbol":      sym,
            "type":        "Cash-Momentum",
            "entry":       entry,
            "cmp":         entry,
            "target":      tgt,
            "sl":          sl,
            "pop":         pop,
            "status":      "Open",
            "pnl":         0.0,
            "action":      "Buy"
        })

    return trades

def save_trades_to_json(trades, path="trades.json"):
    with open(path,"w") as f:
        json.dump(trades, f, indent=2)
