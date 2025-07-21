"""
sniper_engine.py
Cash Long / Cash Short + 1σ OTM SHORT Strangle
Filters: RSI · ADX · IV-Rank ≥33 % · MACD · Volume
         20-bar Donchian breakout & 5-bar squeeze breakout (up or down)
Tags:    RSI✅  MACD✅  DC✅  SQ✅  IVR✅
"""
import json, math, statistics, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils  import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, in_squeeze_breakout, iv_rank
)

N_SIGMA = 1.0
SIGMA_FALLBACKS = [1.25, 1.5]

# ── PASS/FAIL ─────────────────────────────────────────────────────────────
def _validate(symbol, cmp_):
    if cmp_ is None:                  return False
    if fetch_rsi(symbol) < RSI_MIN:   return False
    if fetch_adx(symbol) < ADX_MIN:   return False
    if iv_rank(symbol)   < 0.33:      return False   # ← NEW IV-Rank filter
    if not fetch_macd(symbol):        return False
    if not fetch_volume(symbol):      return False
    return True

def _breakout_dir(symbol, cmp_):
    hi, lo = donchian_high_low(symbol, 20)
    if hi is None: return None
    if cmp_ >= hi and in_squeeze_breakout(symbol, direction="up"):   return "up"
    if cmp_ <= lo and in_squeeze_breakout(symbol, direction="down"): return "down"
    return None

# ── TRADE BUILDERS ───────────────────────────────────────────────────────
def _cash_trade(sym, cmp_, direction):
    long = direction == "up"
    tg   = round(cmp_ * (1.02 if long else 0.98), 2)
    sl   = round(cmp_ * (0.975 if long else 1.025), 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym, "type": "Cash",
        "entry": cmp_, "cmp": cmp_, "target": tg, "sl": sl,
        "pop_pct": DEFAULT_POP,
        "action": "Buy" if long else "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": ["RSI✅","MACD✅","DC✅","SQ✅","IVR✅"],
        "status": "Open", "exit_date": "-", "holding_days": 0, "pnl": 0.0
    }

def _pick_strikes(cmp_, oc, sigma, days):
    band = sigma * math.sqrt(days/365)
    ce = min((s for s in oc["CE"] if s >= cmp_*(1+band)), default=None)
    pe = max((s for s in oc["PE"] if s <= cmp_*(1-band)), default=None)
    return (ce, pe) if ce and pe else None

def _short_strangle(sym, cmp_, oc, sigma, days):
    strikes = _pick_strikes(cmp_, oc, sigma, days)
    if not strikes: return None
    ce, pe = strikes
    credit = round((oc["ltp_map"][ce] + oc["ltp_map"][pe]) / 2, 2)
    return {
        "date": dt.datetime.today().strftime("%Y-%m-%d"),
        "symbol": sym, "type": "Option Strangle",
        "entry": credit, "cmp": credit,
        "target": round(credit*0.70, 2), "sl": round(credit*1.60, 2),
        "pop_pct": f"{int(sigma*100)}%",
        "action": "Sell",
        "sector": fetch_sector_strength(sym),
        "tags": [f"{sigma:.2f}σ","DC✅","SQ✅","IVR✅", oc["expiry"]],
        "options":{
            "expiry": oc["expiry"], "call": ce, "put": pe,
            "call_ltp": oc["ltp_map"][ce], "put_ltp": oc["ltp_map"][pe]
        },
        "status": "Open", "exit_date": "-", "holding_days": 0, "pnl": 0.0
    }

# ── ENGINE LOOP ───────────────────────────────────────────────────────────
def generate_sniper_trades():
    trades=[]
    for sym in FNO_SYMBOLS:
        cmp_ = fetch_cmp(sym)
        if not _validate(sym, cmp_): continue
        direction = _breakout_dir(sym, cmp_)
        if direction is None: continue

        trades.append(_cash_trade(sym, cmp_, direction))

        oc = fetch_option_chain(sym)
        if not oc: continue
        days = oc.get("days_to_exp", 7)
        tr = _short_strangle(sym, cmp_, oc, N_SIGMA, days)
        if not tr:
            for sig in SIGMA_FALLBACKS:
                tr = _short_strangle(sym, cmp_, oc, sig, days)
                if tr: break
        if tr: trades.append(tr)

    print(f"✅ trades: {len(trades)}")
    return trades

def save_trades_to_json(trs):
    with open("trades.json","w",encoding="utf-8") as f: json.dump(trs,f,indent=2)

if __name__ == "__main__":
    save_trades_to_json(generate_sniper_trades())
