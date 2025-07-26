"""
sniper_engine.py

Returns a combined list of:
  1) Options‑Strangles
  2) Futures
  3) Cash‑Momentum
"""
from typing import List, Dict
from datetime import date, timedelta
import math

import utils
from config import RSI_MIN, TOP_N_MOMENTUM, POPCUT
from instruments import FNO_SYMBOLS

MIN_TURNOVER_CR = 50
STRANGLE_DTE    = 30
ATR_WIDTH       = 1.2
TOP_N_STRANG    = 10
TOP_N_FUTURES   = 5

def next_expiry(days_out=STRANGLE_DTE) -> date:
    today=date.today()
    exp=date(today.year,today.month,28)
    while exp.weekday()!=3: exp-=timedelta(days=1)
    if (exp-today).days<days_out:
        m,today_y=today.month+1,today.year
        if m>12: m, today_y=1,today_y+1
        exp=date(today_y,m,28)
        while exp.weekday()!=3: exp-=timedelta(days=1)
    return exp

def generate_sniper_trades() -> List[Dict]:
    today_str=date.today().isoformat()
    exp=next_expiry(); dte=(exp-date.today()).days
    ideas=[]

    # 1) Strangles
    strangs=[]
    for s in FNO_SYMBOLS:
        df=utils.fetch_ohlc(s,60)
        if df is None or df.empty: continue
        if utils.avg_turnover(df)<MIN_TURNOVER_CR: continue
        spot,atr14=df["close"].iloc[-1],utils.atr(df,14).iloc[-1]
        w=ATR_WIDTH*atr14
        put,call=math.floor((spot-w)/50)*50, math.ceil((spot+w)/50)*50
        dp,dc=utils.bs_delta(spot,put,dte,call=False), utils.bs_delta(spot,call,dte,call=True)
        pop=round((1-abs(dp))*(1-abs(dc)),2)
        if pop<POPCUT: continue
        try:
            pt,ct=utils.option_token(s,put,exp,"PE"), utils.option_token(s,call,exp,"CE")
            pp,cp=utils.fetch_option_price(pt),utils.fetch_option_price(ct)
            if pp is None or cp is None: continue
            strangs.append({
                "date":today_str,"symbol":s,"type":"Options-Strangle",
                "put_strike":put,"call_strike":call,
                "put_price":round(pp,2),"call_price":round(cp,2),
                "pop":pop,"status":"Open","action":"Sell"
            })
        except: pass
    ideas+=sorted(strangs,key=lambda x:x["pop"],reverse=True)[:TOP_N_STRANG]

    # 2) Futures
    futs=[]
    for s in FNO_SYMBOLS:
        r=utils.fetch_rsi(s,60)
        if r is None or r<RSI_MIN: continue
        tkn=utils.future_token(s,exp)
        price=utils.fetch_future_price(tkn)
        if price is None: continue
        futs.append({
            "date":today_str,"symbol":s,"type":"Futures",
            "entry":round(price,2),"rsi":round(r,2),
            "status":"Open","action":"Buy"
        })
    ideas+=sorted(futs,key=lambda x:x["rsi"],reverse=True)[:TOP_N_FUTURES]

    # 3) Cash‑Momentum
    mom=[]
    for s in FNO_SYMBOLS:
        r=utils.fetch_rsi(s,60)
        if r is None: continue
        pop=utils.hist_pop(s,2,1) or 0
        if pop<0.5: continue
        mom.append((s,r,pop))
    for s,r,p in sorted(mom,key=lambda x:x[1],reverse=True)[:TOP_N_MOMENTUM]:
        df=utils.fetch_ohlc(s,60)
        if df is None or df.empty: continue
        e=df["close"].iloc[-1]; sl,tk=e*0.99,e*1.02
        ideas.append({
            "date":today_str,"symbol":s,"type":"Cash-Momentum",
            "entry":round(e,2),"SL":round(sl,2),"Target":round(tk,2),
            "PoP":round(p,2),"status":"Open","action":"Buy"
        })
    return ideas
