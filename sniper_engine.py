"""
sniper_engine.py – Cash Long/Short + 1σ OTM SHORT Strangle
Filters: RSI · ADX · IV-Rank ≥33 % (or IV unavailable) · MACD · Volume
Breakouts: 20-bar Donchian + 5-bar squeeze (up/down)
"""
import json, math, datetime as dt
from config import FNO_SYMBOLS, DEFAULT_POP, RSI_MIN, ADX_MIN
from utils  import (
    fetch_cmp, fetch_rsi, fetch_adx, fetch_macd, fetch_volume,
    fetch_sector_strength, fetch_option_chain,
    donchian_high_low, in_squeeze_breakout, iv_rank
)

N_SIGMA = 1.0; SIGMA_FALLBACKS=[1.25,1.5]

def _validate(sym, cmp_):
    if cmp_ is None: return False
    if fetch_rsi(sym) < RSI_MIN or fetch_adx(sym) < ADX_MIN: return False
    ivr=iv_rank(sym);  # allow trade if IV fetch failed (ivr==0) else require ≥0.33
    if ivr and ivr < 0.33: return False
    if not fetch_macd(sym) or not fetch_volume(sym)>1.5: return False
    return True

def _breakout_dir(sym, cmp_):
    hi,lo=donchian_high_low(sym,20)
    if hi and cmp_>=hi and in_squeeze_breakout(sym,direction="up"): return "up"
    if lo and cmp_<=lo and in_squeeze_breakout(sym,direction="down"): return "down"
    return None

def _cash_trade(sym,cmp_,dir):
    long=dir=="up"; tgt=round(cmp_*(1.02 if long else 0.98),2); sl=round(cmp_*(0.975 if long else 1.025),2)
    return {"date":dt.datetime.today().strftime("%Y-%m-%d"),"symbol":sym,"type":"Cash",
            "entry":cmp_,"cmp":cmp_,"target":tgt,"sl":sl,"pop_pct":DEFAULT_POP,
            "action":"Buy" if long else "Sell","sector":fetch_sector_strength(sym),
            "tags":["RSI✅","MACD✅","DC✅","SQ✅","IVR✅"],
            "status":"Open","exit_date":"-","holding_days":0,"pnl":0.0}

def _pick(cmp_,oc,sig,days):
    band=sig*math.sqrt(days/365); ce=min((s for s in oc["CE"] if s>=cmp_*(1+band)),default=None)
    pe=max((s for s in oc["PE"] if s<=cmp_*(1-band)),default=None); return (ce,pe) if ce and pe else None

def _strangle(sym,cmp_,oc,sig,days):
    stk=_pick(cmp_,oc,sig,days);  ce,pe=stk if stk else (None,None)
    if not stk: return None
    cred=round((oc["ltp_map"][ce]+oc["ltp_map"][pe])/2,2)
    return {"date":dt.datetime.today().strftime("%Y-%m-%d"),"symbol":sym,"type":"Option Strangle",
            "entry":cred,"cmp":cred,"target":round(cred*0.70,2),"sl":round(cred*1.60,2),
            "pop_pct":f"{int(sig*100)}%","action":"Sell","sector":fetch_sector_strength(sym),
            "tags":[f"{sig:.2f}σ","DC✅","SQ✅","IVR✅",oc["expiry"]],
            "options":{"expiry":oc["expiry"],"call":ce,"put":pe,
                       "call_ltp":oc["ltp_map"][ce],"put_ltp":oc["ltp_map"][pe]},
            "status":"Open","exit_date":"-","holding_days":0,"pnl":0.0}

def generate_sniper_trades():
    trades=[]
    for sym in FNO_SYMBOLS:
        cmp_=fetch_cmp(sym)
        if not _validate(sym,cmp_): continue
        dir=_breakout_dir(sym,cmp_);  if dir is None: continue
        trades.append(_cash_trade(sym,cmp_,dir))
        oc=fetch_option_chain(sym);  days=oc.get("days_to_exp",7) if oc else 7
        s=_strangle(sym,cmp_,oc,N_SIGMA,days) if oc else None
        if not s:
            for sig in SIGMA_FALLBACKS:
                if oc: s=_strangle(sym,cmp_,oc,sig,days)
                if s: break
        if s: trades.append(s)
    print(f"✅ trades: {len(trades)}"); return trades

def save_trades_to_json(t): open("trades.json","w").write(json.dumps(t,indent=2))

if __name__=="__main__": save_trades_to_json(generate_sniper_trades())
