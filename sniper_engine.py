"""
Sniper Engine – anti-whipsaw edition
"""
from typing import List, Dict
from datetime import date
from instruments import FNO_SYMBOLS
import utils

# thresholds
MIN_TURNOVER_CR   = 50      # ₹Cr
ATR_MIN, ATR_MAX  = 0.01, 0.04
ADX_MIN           = 25
RSI_TRIG          = 55
POP_MIN           = 0.55
TOP_N             = 10
SL_PCT, TGT_PCT   = 2.0, 3.0

def avg_turnover(df, n=20):
    return (df["close"] * df["volume"]).rolling(n).mean().iloc[-1] / 1e7  # ₹Cr

def fetch_cmp(sym):
    utils.gate()
    try:
        return round(utils._kite.ltp(f"NSE:{sym}")[f"NSE:{sym}"]["last_price"], 2)
    except Exception:
        return None

def generate_sniper_trades() -> List[Dict]:
    picks: List[Dict] = []
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 260)        # ~1 year
        if df is None: continue

        cmp_ = df["close"].iloc[-1]
        if cmp_ <= utils.sma(df["close"], 200).iloc[-1]:        # trend filter
            continue
        if avg_turnover(df) < MIN_TURNOVER_CR:                 # liquidity
            continue
        atr_pct = utils.atr(df).iloc[-1] / cmp_
        if not (ATR_MIN <= atr_pct <= ATR_MAX):                # vol sanity
            continue
        if utils.adx(df).iloc[-1] < ADX_MIN:                   # trend strength
            continue

        rsi_val = utils.rsi(df).iloc[-1]
        pop_val = utils.hist_pop(df[-100:], TGT_PCT, SL_PCT)   # 100-day lookback

        if rsi_val >= RSI_TRIG and pop_val and pop_val >= POP_MIN:
            trade = {
                "date":   date.today().isoformat(),
                "symbol": sym,
                "type":   "Cash",
                "entry":  cmp_,
                "cmp":    cmp_,
                "target": round(cmp_ * (1 + TGT_PCT/100), 2),
                "sl":     round(cmp_ * (1 - SL_PCT/100), 2),
                "pop":    pop_val,
                "status": "Open",
                "pnl":    0.0,
                "action": "Buy",
                "rsi":    round(rsi_val, 2),
                "adx":    round(utils.adx(df).iloc[-1], 2),
            }
            picks.append(trade)

    # rank by RSI, keep top N
    picks = sorted(picks, key=lambda x: x["rsi"], reverse=True)[:TOP_N]
    return picks
