"""
utils.py  –  Zerodha + NSE helpers
----------------------------------------------------------------
• fetch_cmp               : last traded price (cash)
• fetch_ohlc              : pandas OHLC dataframe
• donchian_high_low       : 20-bar channel hi/lo
• in_squeeze_breakout     : TTM-style squeeze → breakout (bull OR bear)
• fetch_option_chain      : CE / PE strike lists, LTP map, days_to_exp
• atm_iv, iv_rank         : ATM implied vol & 1-yr IV-Rank (cache)
----------------------------------------------------------------
"""
import os, json, math, pathlib, requests, pandas as pd
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ── Render / local env ────────────────────────────────────────────────────
load_dotenv("config.env", override=False)
API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ╭────────────────────────────────────────────────────────────────────────╮
# │  1.  BASIC MARKET DATA                                                │
# ╰────────────────────────────────────────────────────────────────────────╯
def fetch_cmp(symbol: str):
    try:
        q = kite.ltp(f"NSE:{symbol}")
        return q[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        print(f"❌ CMP {symbol}: {e}")
        return None

def fetch_ohlc(symbol: str, days: int = 60):
    try:
        end, start = dt.today(), dt.today() - timedelta(days=days*2)
        inst = next(i["instrument_token"] for i in kite.instruments("NSE")
                    if i["tradingsymbol"] == symbol)
        data = kite.historical_data(inst, start, end, "day")
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ OHLC {symbol}: {e}")
        return None

# ╭────────────────────────────────────────────────────────────────────────╮
# │  2.  DONCHIAN + SQUEEZE BREAKOUT                                      │
# ╰────────────────────────────────────────────────────────────────────────╯
def donchian_high_low(symbol: str, window: int = 20):
    df = fetch_ohlc(symbol, window + 3)
    if df is None or df.empty: return None, None
    high = df["high"].iloc[-window:].max()
    low  = df["low"].iloc[-window:].min()
    return high, low

def in_squeeze_breakout(symbol: str,
                        window: int = 20,
                        squeeze_bars: int = 5,
                        direction: str = "up") -> bool:
    """
    True if the latest bar breaks out of a <squeeze_bars>-bar squeeze
    'direction' = 'up'  -> close > BB-upper
               = 'down' -> close < BB-lower
    """
    df = fetch_ohlc(symbol, window + squeeze_bars + 5)
    if df is None or len(df) < window + squeeze_bars: return False

    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values

    # Bollinger Bands (SMA ± 2σ)
    sma = pd.Series(close).rolling(window).mean()
    std = pd.Series(close).rolling(window).std()
    bb_up = sma + 2 * std
    bb_dn = sma - 2 * std

    # Keltner Channel (EMA ± 1.5 ATR)
    ema = pd.Series(close).ewm(span=window, adjust=False).mean()
    atr = pd.Series(high - low).rolling(window).mean()
    kc_up = ema + 1.5 * atr
    kc_dn = ema - 1.5 * atr

    sq = (bb_up[-squeeze_bars:] < kc_up[-squeeze_bars:]) & \
         (bb_dn[-squeeze_bars:] > kc_dn[-squeeze_bars:])
    if not sq.all(): return False

    return close[-1] > bb_up.iloc[-1] if direction == "up" else close[-1] < bb_dn.iloc[-1]

# ╭────────────────────────────────────────────────────────────────────────╮
# │  3.  OPTION-CHAIN (CE, PE, LTP MAP)                                   │
# ╰────────────────────────────────────────────────────────────────────────╯
def fetch_option_chain(symbol: str):
    """
    Returns dict with CE/PE strike lists, last prices, expiry meta.
    """
    try:
        today = dt.today().date()
        nfo   = kite.instruments("NFO")

        fut = next(i for i in nfo if i["segment"] == "NFO-FUT"
                   and i["tradingsymbol"].startswith(symbol))
        exp_date = fut["expiry"].date()
        days = (exp_date - today).days
        exp_type = "Weekly" if days <= 10 else "Monthly"

        chain = [i for i in nfo if i["name"] == symbol and i["expiry"].date() == exp_date]
        ltp_json = kite.ltp([f"NFO:{i['tradingsymbol']}" for i in chain])

        ce, pe, ltp_map = [], [], {}
        for ins in chain:
            strike = float(ins["strike"])
            key = f"NFO:{ins['tradingsymbol']}"
            price = ltp_json.get(key, {}).get("last_price", 0)
            ltp_map[strike] = price
            (ce if ins["instrument_type"] == "CE" else pe).append(strike)

        return {
            "expiry": exp_type,
            "days_to_exp": days,
            "CE": sorted(set(ce)),
            "PE": sorted(set(pe)),
            "ltp_map": ltp_map
        }
    except Exception as e:
        print(f"❌ OC {symbol}: {e}")
        return None

# ╭────────────────────────────────────────────────────────────────────────╮
# │  4.  IV-RANK (ATM IV + rolling cache)                                 │
# ╰────────────────────────────────────────────────────────────────────────╯
CACHE_FILE = pathlib.Path(__file__).parent / "iv_cache.json"
_iv_hist   = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}

def atm_iv(symbol: str):
    """Return ATM IV (%) from NSE public JSON (best-effort)."""
    try:
        url  = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        hdrs = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com"
        }
        sess = requests.Session()
        sess.get("https://www.nseindia.com", headers=hdrs, timeout=5)
        data = sess.get(url, headers=hdrs, timeout=10).json()
        uv   = data["records"]["underlyingValue"]
        rows = data["records"]["data"]
        nearest = min(rows, key=lambda r: abs(r["strikePrice"] - uv))
        return float(nearest["CE"]["impliedVolatility"])
    except Exception as e:
        print(f"❌ IV {symbol}: {e}")
        return None

def iv_rank(symbol: str, window: int = 252) -> float:
    """
    IV-Rank percentile (0–1). Stores history in iv_cache.json.
    """
    iv_today = atm_iv(symbol)
    if iv_today is None: return 0.0

    hist = _iv_hist.get(symbol, [])
    hist.append(iv_today)
    if len(hist) > window: hist = hist[-window:]
    _iv_hist[symbol] = hist
    CACHE_FILE.write_text(json.dumps(_iv_hist, indent=2))

    return sum(iv < iv_today for iv in hist) / len(hist)
