"""
utils.py – complete helper library (pandas/numpy only)
"""
import os, json, math, pathlib, requests, time
from datetime import datetime as dt, timedelta

import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ── Zerodha session ───────────────────────────────────────────────────────
load_dotenv("config.env", override=False)
API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")
kite = KiteConnect(api_key=API_KEY); kite.set_access_token(ACCESS_TOKEN)

# ─── 1 · Basic market data ────────────────────────────────────────────────
def fetch_cmp(symbol: str):
    try:  return kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP {symbol}: {e}"); return None

def fetch_ohlc(symbol: str, days: int = 60):
    try:
        end, start = dt.today(), dt.today() - timedelta(days=days*2)
        tok = next(i["instrument_token"] for i in kite.instruments("NSE")
                   if i["tradingsymbol"] == symbol)
        return pd.DataFrame(kite.historical_data(tok, start, end, "day", oi=True))
    except Exception as e:
        print(f"❌ OHLC {symbol}: {e}"); return None

# ─── 2 · Indicators (RSI / MACD / ADX / Volume) ──────────────────────────
def fetch_rsi(symbol, n=14):
    df = fetch_ohlc(symbol, n+20);   diff = df["close"].diff().dropna()
    up = diff.clip(lower=0); down = -diff.clip(upper=0)
    rs = up.rolling(n).mean().iloc[-1] / (down.rolling(n).mean().iloc[-1] + 1e-9)
    return 100 - 100/(1+rs)

def fetch_macd(symbol, f=12, s=26, sig=9):
    df = fetch_ohlc(symbol, s+sig+50); close = df["close"]
    fast = close.ewm(span=f, adjust=False).mean()
    slow = close.ewm(span=s, adjust=False).mean()
    return (fast - slow).iloc[-1] > (fast - slow).ewm(span=sig, adjust=False).mean().iloc[-1]

def fetch_adx(symbol, n=14):
    df = fetch_ohlc(symbol, n+40)
    hi, lo, cl = df["high"], df["low"], df["close"]
    plus = (hi.diff()).clip(lower=0); minus = (-lo.diff()).clip(lower=0)
    plus[plus < minus] = 0; minus[minus < plus] = 0
    tr = pd.concat([hi-lo, (hi-cl.shift()).abs(), (lo-cl.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    pdi, mdi = 100*plus.rolling(n).sum()/atr, 100*minus.rolling(n).sum()/atr
    return (100*((pdi-mdi).abs()/(pdi+mdi))).rolling(n).mean().iloc[-1]

def fetch_volume(symbol, w=20):
    df = fetch_ohlc(symbol, w+5)
    return df["volume"].iloc[-1] / (df["volume"].iloc[-w:].mean()+1e-9)

# ─── 3 · Donchian & squeeze breakout ─────────────────────────────────────
def donchian_high_low(symbol, w=20):
    df = fetch_ohlc(symbol, w+3); return df["high"].iloc[-w:].max(), df["low"].iloc[-w:].min()

def in_squeeze_breakout(symbol, w=20, sq_len=5, direction="up"):
    df = fetch_ohlc(symbol, w+sq_len+5); close, hi, lo = df["close"], df["high"], df["low"]
    sma = close.rolling(w).mean(); std = close.rolling(w).std()
    bb_up, bb_dn = sma+2*std, sma-2*std
    ema, atr = close.ewm(span=w, adjust=False).mean(), (hi-lo).rolling(w).mean()
    kc_up, kc_dn = ema+1.5*atr, ema-1.5*atr
    squeeze = (bb_up[-sq_len:]<kc_up[-sq_len:]) & (bb_dn[-sq_len:]>kc_dn[-sq_len:])
    if not squeeze.all(): return False
    return close.iloc[-1] > bb_up.iloc[-1] if direction=="up" else close.iloc[-1] < bb_dn.iloc[-1]

# ─── 4 · Option-chain helper ─────────────────────────────────────────────
def fetch_option_chain(symbol):
    try:
        today = dt.today().date(); nfo = kite.instruments("NFO")
        fut = next(i for i in nfo if i["segment"]=="NFO-FUT" and i["tradingsymbol"].startswith(symbol))
        exp = fut["expiry"].date(); days=(exp-today).days; etype="Weekly" if days<=10 else "Monthly"
        chain = [i for i in nfo if i["name"]==symbol and i["expiry"].date()==exp]
        ltp = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])
        ce, pe, m = [], [], {}
        for ins in chain:
            s=float(ins["strike"]); m[s]=ltp.get(f"NFO:{ins['tradingsymbol']}",{}).get("last_price",0)
            (ce if ins["instrument_type"]=="CE" else pe).append(s)
        return {"expiry":etype,"days_to_exp":days,"CE":sorted(set(ce)),"PE":sorted(set(pe)),"ltp_map":m}
    except Exception as e:
        print(f"❌ OC {symbol}: {e}"); return None

# ─── 5 · IV & IV-Rank (with retry) ───────────────────────────────────────
CACHE = pathlib.Path(__file__).parent/"iv_cache.json"
_iv = json.loads(CACHE.read_text()) if CACHE.exists() else {}

def atm_iv(symbol, retries=3, pause=1.0):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    hdr = {"User-Agent":"Mozilla/5.0","Accept":"application/json","Referer":"https://www.nseindia.com"}
    sess = requests.Session()
    for _ in range(retries):
        try:
            sess.get("https://www.nseindia.com", headers=hdr, timeout=5)
            data=sess.get(url, headers=hdr, timeout=10).json()
            uv=data["records"]["underlyingValue"]; rows=data["records"]["data"]
            return float(min(rows, key=lambda r:abs(r["strikePrice"]-uv))["CE"]["impliedVolatility"])
        except Exception: time.sleep(pause)
    print(f"❌ IV {symbol}: retries exhausted"); return None

def iv_rank(symbol, win=252):
    iv=atm_iv(symbol);  hist=_iv.get(symbol,[])
    if iv is None: return 0.0
    hist.append(iv); _iv[symbol]=hist[-win:]; CACHE.write_text(json.dumps(_iv,indent=2))
    return sum(x<iv for x in hist)/len(hist)

# ─── 6 · Sector-strength stub ────────────────────────────────────────────
_sector_map={"FINANCIAL":"Leader","BANK":"Leader","IT":"Leader",
             "AUTO":"Neutral","FMCG":"Neutral","MEDIA":"Weak","METAL":"Weak"}

def fetch_sector_strength(symbol):
    try:
        ind=next(i for i in kite.instruments("NSE") if i["tradingsymbol"]==symbol)["industry"].upper()
        for k,v in _sector_map.items():
            if k in ind: return v
    except Exception: pass
    return "Neutral"
