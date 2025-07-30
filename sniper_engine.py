import json
import math
from datetime import date

import joblib
import numpy as np

import utils
from config import (
    FNO_SYMBOLS,
    RSI_MIN,
    ADX_MIN,
    VOL_MULTIPLIER,
    STRANGLE_SD_BANDS,
    SECTOR_POP_EXCEPT
)

# Attempt to load ML model (optional)
try:
    artifact = joblib.load("model.pkl")
    MODEL = artifact["model"]
    THRESH = artifact.get("threshold", 0.5) * 100
    print("✅ Loaded ML model")
except Exception:
    MODEL = None
    THRESH = None
    print("⚠️ ML model not found — using rule‑based only")


def _compute_pop(sym, entry, tgt, sl):
    """
    Compute Probability of Profit, using ML if available, otherwise historical.
    """
    tgt_pct = (tgt - entry) / entry * 100
    sl_pct  = (entry - sl)    / entry * 100

    if MODEL:
        # ML-based PoP
        features = [
            utils.fetch_rsi(sym, 14),
            utils.fetch_adx(sym, 14),
            utils.fetch_atr(sym, 14),
            int(utils.fetch_ohlc(sym, 30)["volume"].iloc[-1] or 0),
            utils.hist_pop(sym, tgt_pct, sl_pct)
        ]
        score = MODEL.predict_proba([features])[0,1] * 100
        return round(score, 2)
    else:
        # Historical PoP only
        return round(utils.hist_pop(sym, tgt_pct, sl_pct), 2)


def generate_sniper_trades():
    """
    Generates Sniper trades applying:
      - F&O existence
      - RSI/ADX filters
      - ICT liquidity‑grab
      - VWAP/OBV confluence
      - Sector rotation gating
      - Short‑strangle setups
      - Probability of Profit checks
    """
    today  = date.today().isoformat()
    trades = []

    # Pre‑compute sector rotation data
    sector_info = utils.fetch_sector_rotation()
    # e.g. {'Banking': {'1d':0.5,'1w':2.1,'strength':'Leader'}, ...}

    for sym in FNO_SYMBOLS:
        # --- data availability ---
        df = utils.fetch_ohlc(sym, days=60)
        if df.empty:
            continue

        # --- RSI & ADX filters ---
        rsi = utils.fetch_rsi(sym, 14)
        adx = utils.fetch_adx(sym, 14)
        if rsi < RSI_MIN or adx < ADX_MIN:
            continue

        # --- F&O existence check ---
        fno_ok = utils.check_fno_exists(sym)
        if not fno_ok:
            continue

        # --- Entry, SL, Target calculation ---
        last  = df["close"].iloc[-1]
        atr   = utils.fetch_atr(sym, 14)
        entry = round(last, 2)
        sl    = round(last - atr * VOL_MULTIPLIER, 2)
        tgt   = round(last + atr * VOL_MULTIPLIER, 2)

        # --- ICT liquidity‑grab ---
        ict_ok = utils.check_ict_liquidity(sym, df)
        if not ict_ok:
            continue

        # --- VWAP & OBV confluence ---
        vwap_ok = utils.check_vwap_confluence(sym)
        obv_ok  = utils.check_obv_confirmation(sym, df)
        if not (vwap_ok and obv_ok):
            continue

        # --- Sector rotation gating ---
        sect      = utils.get_symbol_sector(sym)
        sec_data  = sector_info.get(sect, {})
        strength  = sec_data.get("strength", "Neutral")
        sector_ok = True
        # if sector is weak, require higher PoP to allow
        if strength == "Weak":
            sector_ok = False

        # --- Compute PoP ---
        pop = _compute_pop(sym, entry, tgt, sl)
        if MODEL and pop < THRESH:
            continue
        if not sector_ok and pop < SECTOR_POP_EXCEPT:
            continue

        # --- Short‑strangle setup ---
        strangle = utils.find_short_strangle(sym, bands=STRANGLE_SD_BANDS)
        strangle_ok = bool(strangle)
        if not strangle_ok:
            continue

        # --- Append final trade ---
        trades.append({
            "entry_date":       today,
            "symbol":           sym,
            "type":             "Sniper-Multi",
            "entry":            entry,
            "cmp":              entry,
            "target":           tgt,
            "sl":               sl,
            "pop":              pop,
            "status":           "Open",
            "sector":           sect,
            # diagnostic flags
            "fno_ok":           fno_ok,
            "ict_ok":           ict_ok,
            "vwap_ok":          vwap_ok,
            "obv_ok":           obv_ok,
            "sector_strength":  strength,
            "strangle_ok":      strangle_ok,
            "strangle":         strangle
        })

    return trades


def save_trades_to_json(trades, path="docs/trades.json"):
    """
    Saves the generated trades list to the specified JSON file.
    """
    with open(path, "w") as f:
        json.dump(trades, f, indent=2)


if __name__ == "__main__":
    trades = generate_sniper_trades()
    save_trades_to_json(trades)
    print(f"✅ Saved {len(trades)} trades to docs/trades.json")
