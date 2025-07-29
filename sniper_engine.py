# sniper_engine.py

import joblib
import numpy as np
from datetime import date
from config import FNO_SYMBOLS, TOP_N_MOMENTUM
import utils

# ── 1) Load your ML model + decision threshold ──────────────────────────────
_artifact   = joblib.load("model.pkl")
_model      = _artifact["model"]
_THRESHOLD  = _artifact.get("threshold", 0.5)

def generate_sniper_trades() -> list[dict]:
    """
    Generate Cash‑Momentum trades filtered by ML model probability.
    Each returned trade has no date; entry_date is handled in sniper_run_all.py.
    """
    trades = []
    today_iso = date.today().isoformat()

    print("⚙️  Debug: RSI  ADX   ATR    Vol     PoP    ML‑Prob   for each symbol")
    survivors = []

    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, days=40)
        if df is None or df.empty:
            continue

        # 2) Compute indicators & features
        rsi = utils.fetch_rsi(sym, period=14)
        adx = utils.fetch_adx(sym, period=14)
        atr = utils.fetch_atr(sym, period=14)
        vol = int(df["volume"].iloc[-1])
        entry = float(df["close"].iloc[-1])
        # probability‑of‑profit using same ATR‐based target/sl as a proxy
        tgt_pct = (atr / entry) * 100
        sl_pct  = tgt_pct
        pop = utils.hist_pop(sym, tgt_pct, sl_pct)

        # 3) ML score
        feat = np.array([[rsi, adx, atr, vol, pop]])
        prob = _model.predict_proba(feat)[0,1]

        print(f" • {sym:12s} RSI={rsi:5.1f}  ADX={adx:5.1f}  ATR={atr:6.2f}  "
              f"Vol={vol:,}  PoP={pop:5.2f}%  ML={prob:5.3f}")

        if prob < _THRESHOLD:
            continue

        survivors.append((sym, rsi, df, atr))

    # 4) From ML‑approved survivors, pick top‑N by RSI
    for sym, rsi, df, atr in sorted(survivors, key=lambda x: x[1], reverse=True)[:TOP_N_MOMENTUM]:
        entry = float(round(df["close"].iloc[-1], 2))
        sl    = float(round(entry - atr,       2))
        tgt   = float(round(entry + atr,       2))

        trades.append({
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  entry,
            "cmp":    entry,
            "target": tgt,
            "sl":     sl,
            "pop":    None,        # can be filled if needed
            "status": "Open",
            "pnl":    None,
            "action": "Buy",
            # entry_date will be added by sniper_run_all.py
        })

    return trades
