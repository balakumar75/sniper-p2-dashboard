"""
utils.py  –  Zerodha + NSE helpers
• CMP, OHLC, Donchian, Squeeze
• NEW  atm_iv() + iv_rank()  → IV-Rank filter (cache in iv_cache.json)
"""
import os, math, json, pathlib, requests, pandas as pd
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# ── Kite init ────────────────────────────────────────────────────────────
load_dotenv("config.env", override=False)
API_KEY      = os.getenv("KITE_API_KEY")  or os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN") or os.getenv("ZERODHA_ACCESS_TOKEN")
kite = KiteConnect(api_key=API_KEY); kite.set_access_token(ACCESS_TOKEN)

# ── Basic helpers (CMP, OHLC, Donchian, Squeeze) – unchanged -------------
# … (keep everything you already have up to donchian_high_low & in_squeeze_breakout) …

# ── ==========  IV-RANK SUPPORT  ========================================

CACHE_FILE = pathlib.Path(__file__).parent / "iv_cache.json"
_iv_hist   = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}

def atm_iv(symbol: str):
    """
    Returns ATM implied volatility (%) using NSE's public option-chain JSON.
    None if unavailable or API fails.
    """
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
        underlying = data["records"]["underlyingValue"]
        rows = data["records"]["data"]

        # find strike closest to underlying → pick CE IV
        near = min(rows, key=lambda r: abs(r["strikePrice"] - underlying))
        iv = near["CE"]["impliedVolatility"]
        return float(iv)
    except Exception as e:
        print(f"❌ IV fetch {symbol}: {e}")
        return None

def iv_rank(symbol: str, window: int = 252) -> float:
    """
    Returns IV-Rank (0‒1). Keeps a rolling <window> history per symbol.
    """
    iv_today = atm_iv(symbol)
    if iv_today is None: return 0.0

    hist = _iv_hist.get(symbol, [])
    hist.append(iv_today)
    if len(hist) > window: hist = hist[-window:]
    _iv_hist[symbol] = hist
    CACHE_FILE.write_text(json.dumps(_iv_hist, indent=2))

    rank = sum(iv < iv_today for iv in hist) / len(hist)
    return rank
