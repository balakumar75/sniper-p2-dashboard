"""
Global rate-limit patch for KiteConnect.
Import *once* before you create the KiteConnect object.
"""

from functools import wraps
from kiteconnect import KiteConnect
from rate_limiter import gate   # already exists

def _rl(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        gate()                  # wait if we’re at the limit
        return fn(*args, **kwargs)
    return wrapper

# Patch the heavy-traffic endpoints
KiteConnect.historical_data = _rl(KiteConnect.historical_data)
KiteConnect.quote          = _rl(KiteConnect.quote)
KiteConnect.ltp            = _rl(KiteConnect.ltp)
