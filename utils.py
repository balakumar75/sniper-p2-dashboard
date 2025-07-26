#!/usr/bin/env python3
"""
utils.py

Data‐fetch, indicators, helpers for options & futures.
"""
import time, datetime as dt, math
import pandas as pd
from kiteconnect import exceptions as kc_ex
from rate_limiter import gate
from instruments import SYMBOL_TO_TOKEN, OPTION_TOKENS, FUTURE_TOKENS

_kite = None
def set_kite(k): global _kite; _kite = k

def _today(): return dt.date.today()
def _days_ago(d): return _today() - dt.timedelta(days=d)

def token(sym): return SYMBOL_TO_TOKEN[sym]

def fetch_ohlc(sym: str, days: int) -> pd.DataFrame | None:
    if _kite is None: raise RuntimeError("set_kite not called")
    for i in range(5):
        gate()
        try:
            data = _kite.historical_data(token(sym), _days_ago(days), _today(), interval="day")
            df = pd.DataFrame(data)
            return df if not df.empty else None
        except kc_ex.InputException as e:
            if "Too many requests" in str(e): time.sleep(2**i); continue
            return None
        except: return None
    return None

# ── Core indicators ─────────────────────────────────────────────────────────
def atr(df, n=14):
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def adx(df, n=14):
    up, down = df["high"].diff(), -df["low"].diff()
    plus_dm  = up.where((up>down)&(up>0), 0.0)
    minus_dm = down.where((down>up)&(down>0),0.0)
    hl, hc, lc = df["high"]-df["low"], (df["high"]-df["close"].shift()).abs(), (df["low"]-df["close"].shift()).abs()
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    atr14 = tr.rolling(n).mean()
    plus_di  = 100*plus_dm.rolling(n).sum()/atr14
    minus_di = 100*minus_dm.rolling(n).sum()/atr14
    dx = (plus_di-minus_di).abs()/(plus_di+minus_di)*100
    return dx.rolling(n).mean()

def rsi(df, n=14):
    diff = df["close"].diff().dropna()
    up, dn = diff.clip(lower=0), -diff.clip(upper=0)
    rs = up.rolling(n).mean()/dn.rolling(n).mean()
    return 100 - 100/(1+rs)

# ── Historical PoP (your real logic) ─────────────────────────────────────────
def hist_pop(symbol, tgt_pct, sl_pct, lookback_days=90):
    # TODO: implement actual back-test PoP
    return None

def avg_turnover(df, n=20):
    if df is None or df.empty: return 0.0
    return round((df["close"]*df["volume"]).rolling(n).mean().iloc[-1]/1e7,2)

# ── Black‑Scholes delta ──────────────────────────────────────────────────────
def norm_cdf(x): return (1+math.erf(x/math.sqrt(2)))/2
def bs_delta(spot,strike,dte,call=True,vol=0.25,r=0.05):
    t=dte/365
    d1=(math.log(spot/strike)+(r+0.5*vol**2)*t)/(vol*math.sqrt(t))
    return (math.exp(-r*t)*norm_cdf(d1)) if call else (-math.exp(-r*t)*norm_cdf(-d1))

# ── Tokens & prices ─────────────────────────────────────────────────────────
def option_token(sym,strike,expiry,otype):
    exp = expiry.isoformat() if not isinstance(expiry,str) else expiry
    return OPTION_TOKENS[sym][exp][otype].get(strike,0)

def future_token(sym,expiry):
    exp = expiry.isoformat() if not isinstance(expiry,str) else expiry
    return FUTURE_TOKENS[sym].get(exp,0)

def fetch_option_price(tkn):
    if not tkn or _kite is None: return None
    key=f"NFO:{tkn}"; r=_kite.ltp(key); return r[key]["last_price"]

def fetch_future_price(tkn):
    if not tkn or _kite is None: return None
    key=f"NFO:{tkn}"; r=_kite.ltp(key); return r[key]["last_price"]

# ── Helpers: single‑value indicators ─────────────────────────────────────────
def fetch_rsi(sym,days=60,n=14):
    df=fetch_ohlc(sym,days); return None if df is None else rsi(df,n).iloc[-1]

def fetch_adx(sym,days=60,n=14):
    df=fetch_ohlc(sym,days); return None if df is None else adx(df,n).iloc[-1]

def fetch_macd(sym,days=60,fast=12,slow=26,signal=9):
    df=fetch_ohlc(sym,days)
    if df is None: return None
    e1, e2 = df["close"].ewm(span=fast,adjust=False).mean(), df["close"].ewm(span=slow,adjust=False).mean()
    macd, sig = e1-e2, (e1-e2).ewm(span=signal,adjust=False).mean()
    return (macd-sig).iloc[-1]
