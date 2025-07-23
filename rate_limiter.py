import time
from collections import deque

MAX_CALLS_PER_SEC = 1.2      # safe budget
MAX_CALLS_PER_MIN = 70

_sec, _min = deque(), deque()

def _prune(now, dq, span):
    while dq and now - dq[0] > span:
        dq.popleft()

def gate():
    now = time.time()
    _prune(now, _sec, 1.0)
    _prune(now, _min, 60.0)

    while (len(_sec) >= MAX_CALLS_PER_SEC or
           len(_min) >= MAX_CALLS_PER_MIN):
        time.sleep(0.25)
        now = time.time()
        _prune(now, _sec, 1.0)
        _prune(now, _min, 60.0)

    _sec.append(now)
    _min.append(now)


# Optional helper that retries historical_data 5× with back-off
from kiteconnect import exceptions
def safe_hist(kite, token, start, end, interval):
    for attempt in range(5):
        gate()
        try:
            return kite.historical_data(token, start, end, interval)
        except exceptions.InputException as e:
            if "Too many requests" in str(e):
                time.sleep(2 ** attempt)  # 1 s, 2 s, 4 s…
                continue
            raise
    raise RuntimeError(f"hist retry failed for {token}")
