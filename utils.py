import math
from datetime import date, timedelta
import pandas as pd
from instruments import SYMBOL_TO_TOKEN, FUTURE_TOKENS, OPTION_TOKENS

# ── Global Kite instance ────────────────────────────────────────────────────
kite = None
def set_kite(k):
    """Inject the authenticated KiteConnect instance."""
    global kite
    kite = k

# ── 1) Fetch historical OHLC ─────────────────────────────────────────────────
def fetch_ohlc(symbol: str, n_days: int) -> pd.DataFrame | None:
    """
    Returns the last n_days of daily OHLC for `symbol`, or None on error.
    """
    token = SYMBOL_TO_TOKEN.get(symbol, 0)
    if not token:
        print(f"❌ OHLC {symbol}: no instrument token")
        return None

    end   = date.today()
    start = end - timedelta(days=n_days)
    try:
        data = kite.historical_data(token, start.isoformat(), end.isoformat(), "day")
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    except Exception as e:
        print(f"❌ OHLC {symbol}: {e}")
        return None

# ── 2) Technical indicators ───────────────────────────────────────────────────
def fetch_rsi(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, period + 20)
    if df is None or len(df) < period:
        return 0.0
    diff = df["close"].diff().dropna()
    up   = diff.clip(lower=0).rolling(period).mean()
    down = (-diff.clip(upper=0)).rolling(period).mean()
    if down.iloc[-1] == 0:
        return 100.0
    rs = up.iloc[-1] / down.iloc[-1]
    return 100 - (100 / (1 + rs))

def fetch_adx(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, period * 3)
    if df is None or len(df) < period * 3:
        return 0.0
    # Simple ADX calculation
    from ta.trend import ADXIndicator
    adx = ADXIndicator(df["high"], df["low"], df["close"], period).adx()
    return float(adx.iloc[-1])

def fetch_macd(symbol: str) -> tuple[float, float, float]:
    df = fetch_ohlc(symbol, 60)
    if df is None or len(df) < 26:
        return (0.0, 0.0, 0.0)
    exp12   = df["close"].ewm(span=12).mean()
    exp26   = df["close"].ewm(span=26).mean()
    macd    = exp12 - exp26
    signal  = macd.ewm(span=9).mean()
    hist    = macd - signal
    return (float(macd.iloc[-1]), float(signal.iloc[-1]), float(hist.iloc[-1]))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low   = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close  = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def hist_pop(symbol: str,
             tgt_pct: float,
             sl_pct: float,
             lookback_days: int = 90) -> float:
    df = fetch_ohlc(symbol, lookback_days)
    if df is None or df.empty:
        return 0.0
    wins = total = 0
    for i in range(len(df) - 1):
        entry  = df["close"].iloc[i]
        high   = df["high"].iloc[i+1]
        low    = df["low"].iloc[i+1]
        target = entry * (1 + tgt_pct/100)
        sl_val = entry * (1 - sl_pct/100)
        if high >= target:
            wins += 1
        total += 1
    return round(wins/total, 2) if total else 0.0

def bs_delta(spot: float,
             strike: float,
             t: float,
             r: float = 0.0,
             vol: float = 0.0,
             call: bool = True) -> float:
    if vol == 0 or t == 0:
        return 0.0
    d1 = (math.log(spot/strike) + (r + 0.5 * vol**2) * t) / (vol * math.sqrt(t))
    def N(x): return 0.5 * (1 + math.erf(x/math.sqrt(2)))
    return N(d1) if call else N(d1) - 1

# ── 2.5) Average turnover for filtering ──────────────────────────────────────
def avg_turnover(df: pd.DataFrame) -> float:
    """
    Returns the average daily turnover (volume * close) from the DataFrame.
    """
    if df is None or df.empty:
        return 0.0
    turnover = df["volume"] * df["close"]
    return float(turnover.mean())

# ── 3) Token lookups ─────────────────────────────────────────────────────────
def future_token(symbol: str, expiry: str) -> int:
    return FUTURE_TOKENS.get(symbol, {}).get(expiry, 0)

def option_token(symbol: str,
                 strike: float,
                 expiry: str,
                 otype: str) -> int:
    return OPTION_TOKENS.get(symbol, {}) \
                        .get(expiry, {}) \
                        .get(otype, {}) \
                        .get(strike, 0)

# ── 4) LTP fetchers ──────────────────────────────────────────────────────────
def fetch_future_price(token: int) -> float | None:
    """
    Return the last traded price for the future with instrument_token `token`.
    """
    try:
        res = kite.ltp([token])
        return float(res.get(str(token), {}).get("last_price", 0.0))
    except Exception as e:
        print(f"❌ FUT {token}: {e}")
        return None

def fetch_option_price(token: int) -> float | None:
    """
    Return the last traded price for the option with instrument_token `token`.
    """
    try:
        res = kite.ltp([token])
        return float(res.get(str(token), {}).get("last_price", 0.0))
    except Exception as e:
        print(f"❌ OPT {token}: {e}")
        return None
