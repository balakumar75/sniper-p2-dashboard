# utils.py

import datetime
import pandas as pd
import numpy as np
import math

# ── Global Kite client ─────────────────────────────────────────────────────
_kite = None

def set_kite(k):
    """
    Inject the authenticated KiteConnect instance.
    Must be called once from sniper_run_all.py.
    """
    global _kite
    _kite = k

# ── OHLC fetcher ────────────────────────────────────────────────────────────
def fetch_ohlc(symbol: str, days: int):
    """
    Returns a DataFrame of daily OHLC for the past `days` sessions.
    """
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")

    from instruments import SYMBOL_TO_TOKEN
    token = SYMBOL_TO_TOKEN.get(symbol)
    if not token:
        return None

    to_dt   = datetime.date.today()
    from_dt = to_dt - datetime.timedelta(days=days)
    data = _kite.historical_data(
        instrument_token=token,
        from_date=from_dt.isoformat(),
        to_date=to_dt.isoformat(),
        interval="day"
    )
    if not data:
        return None

    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

# ── Wilder RSI ──────────────────────────────────────────────────────────────
def fetch_rsi(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=100)
    if df is None or len(df) < period+1:
        return 0.0

    delta = df["close"].diff().dropna()
    up    = delta.clip(lower=0)
    down  = -delta.clip(upper=0)
    ma_up   = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up.iloc[-1] / ma_down.iloc[-1] if ma_down.iloc[-1] != 0 else np.inf
    return float(100 - (100 / (1 + rs)))

# ── Wilder ADX ──────────────────────────────────────────────────────────────
def fetch_adx(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=100)
    if df is None or len(df) < period*2:
        return 0.0

    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move   = high.diff()
    down_move = -low.diff()
    plus_dm   = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm  = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    atr       = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di   = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean()  / atr)
    minus_di  = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)

    dx        = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx       = dx.ewm(alpha=1/period, adjust=False).mean()

    val = adx.iloc[-1]
    return float(val) if not np.isnan(val) else 0.0

# ── Simple ATR ─────────────────────────────────────────────────────────────
def fetch_atr(symbol: str, period: int = 14) -> float:
    df = fetch_ohlc(symbol, days=period*3)
    if df is None or len(df) < period+1:
        return 0.0

    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    val = atr.iloc[-1]
    return float(val) if not np.isnan(val) else 0.0

# ── Historical Probability-of-Profit ───────────────────────────────────────
def hist_pop(symbol: str, tgt_pct: float, sl_pct: float, lookback_days: int = 90) -> float:
    df = fetch_ohlc(symbol, days=lookback_days+2)
    if df is None or df.empty:
        return 0.0
    ret = df["close"].pct_change().dropna() * 100
    hits = ret.abs() <= tgt_pct
    return float(hits.sum() / len(ret))

# ── Option token lookup & price fetchers ───────────────────────────────────
def option_token(symbol: str, strike: float, expiry: str, opt_type: str) -> int | None:
    """
    Lookup our pre-fetched OPTION_TOKENS structure.
    """
    from instruments import OPTION_TOKENS
    return OPTION_TOKENS.get(symbol, {}) \
                        .get(expiry, {}) \
                        .get(opt_type, {}) \
                        .get(strike)

def fetch_option_price(token: int) -> float | None:
    """
    Fetch the LTP for a single option instrument.
    """
    if _kite is None:
        raise RuntimeError("utils.set_kite(kite) not called")
    key = f"NSE:{token}"
    res = _kite.ltp([key])
    return float(res.get(key, {}).get("last_price"))

# ── Add any other helpers below (e.g. futures price, Greeks, etc.) ─────────
