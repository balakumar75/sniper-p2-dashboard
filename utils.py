"""
utils.py  –  complete helper library
----------------------------------------------------------------
• Market data : fetch_cmp, fetch_ohlc
• Indicators  : fetch_rsi, fetch_macd, fetch_adx, fetch_volume
• Breakouts   : donchian_high_low, in_squeeze_breakout
• Options     : fetch_option_chain
• Vol metrics : atm_iv, iv_rank  (rolling IV-Rank cache)
----------------------------------------------------------------
Implementation uses only pandas / numpy – no external TA-Lib dependency.
"""
import os, json, math, pathlib, requests
from datetime import datetime as dt, timedelta

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ── Init Zerodha session ──────────────────────────────────────────────────
load_dotenv("config.env", override=False)
API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ╭────────────────────────────────────────────────────────────────────────╮
# │ 1. BASIC MARKET DATA                                                  │
# ╰────────────────────────────────────────────────────────────────────────╯
def fetch_cmp(symbol: str):
    try:
        q = kite.ltp(f"NSE:{symbol}")
        return q[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP {symbol}: {e}")
        return None

def fetch_ohlc(symbol: str, days: int = 60) -> pd.DataFrame | None:
    """Daily OHLCV dataframe (oldest → newest)."""
    try:
        end, start = dt.today(), dt.today() - timedelta(days=days*2)
        token = next(i["instrument_token"] for i in kite.instruments("NSE")
                     if i["tradingsymbol"] == symbol)
        data = kite.historical_data(token, start, end, "day", oi=True)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ OHLC {symbol}: {e}")
        return None

# ╭────────────────────────────────────────────────────────────────────────╮
# │ 2. INDICATORS                                                         │
# ╰────────────────────────────────────────────────────────────────────────╯
def fetch_rsi(symbol: str, period: int = 14):
    df = fetch_ohlc(symbol, period + 20)
    if df is None or df.empty: return 0
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0)
    down = -diff.clip(upper=0)
    roll_up   = up.rolling(period).mean()
    roll_down = down.rolling(period).mean()
    rs = roll_up.iloc[-1] / (roll_down.iloc[-1] + 1e-9)
    return 100 - 100/(1 + rs)

def fetch_macd(symbol: str, fast: int = 12, slow: int = 26, signal: int = 9):
    df = fetch_ohlc(symbol, slow + signal + 50)
    if df is None or df.empty: return False
    close = df["close"]
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line.iloc[-1] > macd_signal.iloc[-1]

def fetch_adx(symbol: str, period: int = 14):
    df = fetch_ohlc(symbol, period + 40)
    if df is None or len(df) < period + 1: return 0
    high, low, close = df["high"], df["low"], df["close"]

    plus_dm  = (high.diff()).clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    plus_dm[plus_dm < minus_dm] = 0
    minus_dm[minus_dm < plus_dm] = 0
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    plus_di  = 100 * (plus_dm.rolling(period).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(period).sum() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return dx.rolling(period).mean().iloc[-1]

def fetch_volume(symbol: str, window: int = 20):
    df = fetch_ohlc(symbol, window + 5)
    if df is None or df.empty: return 0
    vol_today = df["volume"].iloc[-1]
    vol_avg   = df["volume"].iloc[-window:].mean()
    return vol_today / (vol_avg + 1e-9)

# ╭────────────────────────────────────────────────────────────────────────╮
# │ 3. DONCHIAN + SQUEEZE BREAKOUT                                        │
# ╰────────────────────────────────────────────────────────────────────────╯
def donchian_high_low(symbol: str, window: int = 20):
    df = fetch_ohlc(symbol, window + 3)
    if df is None or df.empty: return None, None
    return df["high"].iloc[-window:].max(), df["low"].iloc[-window:].min()

def in_squeeze_breakout(symbol: str,
                        window: int = 20,
                        squeeze_bars: int = 5,
                        direction: str = "up") -> bool:
    df = fetch_ohlc(symbol, window + squeeze_bars + 5)
    if df is None or len(df) < window + squeeze_bars: return False
    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values

    sma = pd.Series(close).rolling(window).mean()
    std = pd.Series(close).rolling(window).std()
    bb_up = sma + 2 * std
    bb_dn = sma - 2 * std

    ema = pd.Series(close).ewm(span=window, adjust=False).mean()
    atr = pd.Series(high - low).rolling(window).mean()
    kc_up = ema + 1.5 * atr
    kc_dn = ema - 1.5 * atr

    sq = (bb_up[-squeeze_bars:] < kc_up[-squeeze_bars:]) & \
         (bb_dn[-squeeze_bars:] > kc_dn[-squeeze_bars:])
    if not sq.all(): return False

    return close[-1] > bb_up.iloc[-1] if direction == "up" else close[-1] < bb_dn.iloc[-1]

# ╭────────────────────────────────────────────────────────────────────────╮
# │ 4. OPTION-CHAIN                                                       │
# ╰────────────────────────────────────────────────────────────────────────╯
def fetch_option_chain(symbol: str):
    try:
        today = dt.today().date()
        nfo = kite.instruments("NFO")
        fut = next(i for i in nfo if i["segment"] == "NFO-FUT"
                   and i["tradingsymbol"].startswith(symbol))
        exp = fut["expiry"].date()
        days = (exp - today).days
        exp_type = "Weekly" if days <= 10 else "Monthly"

        chain = [i for i in nfo if i["name"] == symbol and i["expiry"].date() == exp]
        ltp = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])

        ce, pe, ltp_map = [], [], {}
        for ins in chain:
            strike = float(ins["strike"])
            price  = ltp.get(f"NFO:{ins['tradingsymbol']}", {}).get("last_price", 0)
            ltp_map[strike] = price
            (ce if ins["instrument_type"] == "CE" else pe).append(strike)

        return {
            "expiry": exp_type, "days_to_exp": days,
            "CE": sorted(set(ce)), "PE": sorted(set(pe)),
            "ltp_map": ltp_map
        }
    except Exception as e:
        print(f"❌ OC {symbol}: {e}")
        return None

# ╭────────────────────────────────────────────────────────────────────────╮
# │ 5. IV & IV-RANK                                                       │
# ╰────────────────────────────────────────────────────────────────────────╯
CACHE_FILE = pathlib.Path(__file__).parent / "iv_cache.json"
_iv_hist = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}

def atm_iv(symbol: str):
    try:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        hdr = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com"
        }
        sess = requests.Session()
        sess.get("https://www.nseindia.com", headers=hdr, timeout=5)
        data = sess.get(url, headers=hdr, timeout=10).json()
        uv = data["records"]["underlyingValue"]
        rows = data["records"]["data"]
        nearest = min(rows, key=lambda r: abs(r["strikePrice"] - uv))
        return float(nearest["CE"]["impliedVolatility"])
    except Exception as e:
        print(f"❌ IV {symbol}: {e}")
        return None

def iv_rank(symbol: str, window: int = 252) -> float:
    iv_today = atm_iv(symbol)
    if iv_today is None: return 0.0

    hist = _iv_hist.get(symbol, [])
    hist.append(iv_today)
    if len(hist) > window: hist = hist[-window:]
    _iv_hist[symbol] = hist
    CACHE_FILE.write_text(json.dumps(_iv_hist, indent=2))

    return sum(iv < iv_today for iv in hist) / len(hist)
