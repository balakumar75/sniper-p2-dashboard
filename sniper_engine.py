"""
sniper_engine.py
1) Naked short‐strangles
2) Futures momentum
3) RSI fallback (Cash)
"""
from typing import List, Dict
from datetime import date, timedelta
import math

from instruments import FNO_SYMBOLS, SYMBOL_TO_TOKEN, FUTURE_TOKENS
import utils

# ── PARAMETERS ──────────────────────────────────────────────────────────────
MIN_TURNOVER_CR = 50      # ₹Cr (20-day avg)
STRANGLE_DTE    = 30
ATR_WIDTH       = 1.2
POPCUT          = 0.60
TOP_N_STRANG    = 10

RSI_THRESHOLD   = 55
TOP_N_FUT       = 5       # max futures ideas

RSI_FALLBACK_N  = 5       # cash fallback
SL_PCT          = 2.0
TGT_PCT         = 3.0

# ── Expiry finder (last Thursday) ────────────────────────────────────────────
def next_expiry(days_out=STRANGLE_DTE):
    today = date.today()
    e = date(today.year, today.month, 28)
    while e.weekday() != 3:
        e -= timedelta(days=1)
    if (e - today).days < days_out:
        m = today.month + 1
        y = today.year + (m // 13)
        m = m if m <= 12 else 1
        e = date(y, m, 28)
        while e.weekday() != 3:
            e -= timedelta(days=1)
    return e

def norm_cdf(x): return (1 + math.erf(x/math.sqrt(2))) / 2
def bs_delta(spot, strike, dte, call=True, vol=0.25, r=0.05):
    t = dte/365
    d1 = (math.log(spot/strike)+(r+0.5*vol*vol)*t)/(vol*math.sqrt(t))
    return math.exp(-r*t)*norm_cdf(d1) if call else -math.exp(-r*t)*norm_cdf(-d1)

def round_down(x, s): return int(x//s*s)
def round_up(x,   s): return int(math.ceil(x/s)*s)

def generate_sniper_trades() -> List[Dict]:
    today = date.today().isoformat()
    df_map: Dict[str, any] = {}
    strangles, futures = [], []

    # 1) Build 60-day DF and generate Strangles
    for sym in FNO_SYMBOLS:
        df = utils.fetch_ohlc(sym, 60)
        if df is None or df.empty:
            continue
        df_map[sym] = df

        # liquidity
        turn = (df["close"]*df["volume"]).rolling(20).mean().iloc[-1]/1e7
        if turn < MIN_TURNOVER_CR:
            continue

        spot  = df["close"].iloc[-1]
        atr14 = utils.atr(df,14).iloc[-1]
        width = ATR_WIDTH * atr14
        put   = round_down(spot-width,50)
        call  = round_up(spot+width,50)
        exp   = next_expiry()
        dte   = (exp-date.today()).days

        dp = bs_delta(spot,put, dte, call=False)
        dc = bs_delta(spot,call,dte, call=True)
        combo = round((1-abs(dp))*(1-abs(dc)),2)
        if combo >= POPCUT:
            strangles.append({
                "date":   today, "symbol": sym,
                "type":   "Options-Strangle",
                "entry":  0.0,   "cmp": round(spot,2),
                "target": 0.0,   "sl": 0.0,   "pop": combo,
                "status": "Open","pnl": 0.0,  "action": "Sell",
            })

    if strangles:
        return sorted(strangles, key=lambda t: t["pop"], reverse=True)[:TOP_N_STRANG]

    # 2) Futures momentum (next-month contracts)
    exp = next_expiry(0)
    dte = (exp-date.today()).days
    for sym, df in df_map.items():
        # need FUTURE_TOKENS[sym][exp] → integer token
        tok = FUTURE_TOKENS.get(sym, {}).get(exp)
        if not tok:
            continue

        rsi_val = utils.rsi(df,14).iloc[-1]
        if rsi_val < RSI_THRESHOLD:
            continue

        # get futures LTP
        try:
            quote = utils._kite.ltp(f"NSE:FUT{tok}")
            price = round(quote[f"NSE:FUT{tok}"]["last_price"],2)
        except:
            continue

        stop = round(price*(1-SL_PCT/100),2)
        tgt  = round(price*(1+TGT_PCT/100),2)
        # simple PoP via hist_pop on underlying
        popv = utils.hist_pop(sym,TGT_PCT,SL_PCT) or 0.0

        futures.append({
            "date":   today,    "symbol": f"{sym}-FUT",
            "type":   "Futures", "entry": price,
            "cmp":    price,    "target": tgt,
            "sl":     stop,     "pop":   popv,
            "status": "Open",   "pnl":   0.0,
            "action": "Buy",
        })

    if futures:
        return sorted(futures, key=lambda t: t["pop"], reverse=True)[:TOP_N_FUT]

    # 3) RSI fallback with real PoP
    scored = [(sym, utils.rsi(df,14).iloc[-1]) for sym,df in df_map.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    fallback = []
    for sym,_ in scored[:RSI_FALLBACK_N]:
        df90 = utils.fetch_ohlc(sym,90+1)
        if df90 is None or df90.empty: continue

        prev = df90["close"].shift(1).iloc[1:]
        highs= df90["high"].iloc[1:]
        wins =(highs>=prev*(1+TGT_PCT/100)).sum()
        popv = round(wins/90,2)

        price= prev.iloc[-1]
        fallback.append({
            "date":   today,"symbol":sym,
            "type":   "Cash-Momentum",
            "entry":  round(price,2),"cmp":round(price,2),
            "target": round(price*(1+TGT_PCT/100),2),
            "sl":     round(price*(1-SL_PCT/100),2),
            "pop":    popv,     "status":"Open",
            "pnl":    0.0,      "action":"Buy",
        })

    return fallback
