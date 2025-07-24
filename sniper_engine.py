"""
sniper_engine.py
Strangles + RSI-fallback with simple PoP calculation (no more zeros)
"""
from typing import List, Dict
from datetime import date, timedelta
import math

from instruments import FNO_SYMBOLS
import utils

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50      # ₹Cr (20-day avg)
STRANGLE_DTE    = 30      # days until expiry
ATR_WIDTH       = 1.2     # ±1.2×ATR
POPCUT          = 0.60    # require ≥60% combo PoP
TOP_N_STRANG    = 10      # max strangles
RSI_FALLBACK_N  = 5       # fallback top-5 RSI stocks
SL_PCT          = 2.0     # stock SL %
TGT_PCT         = 3.0     # stock TGT %
LOOKBACK_DAYS   = 90      # for PoP calc

# ── EXPIRY finder ───────────────────────────────────────────────────────────
def next_expiry(days_out=STRANGLE_DTE):
    today = date.today()
    e = date(today.year, today.month, 28)
    while e.weekday() != 3: e -= timedelta(days=1)
    if (e - today).days < days_out:
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        e = date(y, m, 28)
        while e.weekday() != 3: e -= timedelta(days=1)
    return e

# ── Black–Scholes Δ & norm_CDF ──────────────────────────────────────────────
def norm_cdf(x): return (1 + math.erf(x / math.sqrt(2))) / 2
def bs_delta(spot,strike,dte,call=True,vol=0.25,r=0.05):
    t = dte/365
    d1 = (math.log(spot/strike)+(r+0.5*vol*vol)*t)/(vol*math.sqrt(t))
    return math.exp(-r*t)*norm_cdf(d1) if call else -math.exp(-r*t)*norm_cdf(-d1)

def round_down(x, step): return int(x//step*step)
def round_up(x,   step): return int(math.ceil(x/step)*step)

# ── MAIN generator ──────────────────────────────────────────────────────────
def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    strangles: List[Dict] = []
    df_map: Dict[str, any] = {}

    # 1) Build 60-day OHLC per symbol & try strangles
    for sym in FNO_SYMBOLS:
        df60 = utils.fetch_ohlc(sym, 60)
        if df60 is None or df60.empty:
            continue
        df_map[sym] = df60

        avg_turn = (df60["close"]*df60["volume"]).rolling(20).mean().iloc[-1]/1e7
        if avg_turn < MIN_TURNOVER_CR:
            continue

        spot  = df60["close"].iloc[-1]
        atr14 = utils.atr(df60,14).iloc[-1]
        width = ATR_WIDTH*atr14

        put_strike  = round_down(spot-width,50)
        call_strike = round_up(spot+width,50)

        exp = next_expiry()
        dte = (exp-date.today()).days

        dp = bs_delta(spot,put_strike,dte,call=False)
        dc = bs_delta(spot,call_strike,dte,call=True)
        combo = round((1-abs(dp))*(1-abs(dc)),2)

        if combo >= POPCUT:
            strangles.append({
                "date":   today,
                "symbol": sym,
                "type":   "Options-Strangle",
                "entry":  0.0,
                "cmp":    round(spot,2),
                "target": 0.0,
                "sl":     0.0,
                "pop":    combo,
                "status": "Open",
                "pnl":    0.0,
                "action": "Sell",
            })

    if strangles:
        return sorted(strangles, key=lambda x: x["pop"], reverse=True)[:TOP_N_STRANG]

    # 2) Fallback -> top-RSI with **simple** PoP
    scored = []
    for sym, df60 in df_map.items():
        r = utils.rsi(df60,14).iloc[-1]
        scored.append((sym,r))
    scored.sort(key=lambda x: x[1], reverse=True)

    fallback: List[Dict] = []
    for sym,r in scored[:RSI_FALLBACK_N]:
        df90 = utils.fetch_ohlc(sym, LOOKBACK_DAYS+1)
        if df90 is None or df90.empty: continue

        # simple PoP = % of days high >= prev_close*(1+TGT_PCT)
        prev = df90["close"].shift(1).iloc[1:]
        highs = df90["high"].iloc[1:]
        wins = (highs >= prev*(1+TGT_PCT/100)).sum()
        pop  = round(wins / LOOKBACK_DAYS,2)

        price = prev.iloc[-1]
        fallback.append({
            "date":   today,
            "symbol": sym,
            "type":   "Cash-Momentum",
            "entry":  round(price,2),
            "cmp":    round(price,2),
            "target": round(price*(1+TGT_PCT/100),2),
            "sl":     round(price*(1-SL_PCT/100),2),
            "pop":    pop,
            "status": "Open",
            "pnl":    0.0,
            "action": "Buy",
        })

    return fallback
