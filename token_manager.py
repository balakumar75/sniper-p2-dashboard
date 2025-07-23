import os, json, datetime
from kiteconnect import KiteConnect, exceptions

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TOKENS_FILE = "tokens.json"               # local cache (auto-updated)
API_KEY     = os.getenv("KITE_API_KEY")
API_SECRET  = os.getenv("KITE_API_SECRET")

# ---------------------------------------------------------------------------
# Helpers to load / save the cached tokens file
# ---------------------------------------------------------------------------
def _load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------------------------------
# Headless login stub (only used if no refresh_token available)
# ---------------------------------------------------------------------------
def _headless_login(kite: KiteConnect):
    """
    If both access_token and refresh_token are missing/invalid,
    fall back to an automated browser login.
    Implement your Selenium / PyOTP flow here when ready.
    """
    def fetch_request_token_somehow():
        raise RuntimeError("Headless login not implemented")
    req_token = fetch_request_token_somehow()
    sess = kite.generate_session(req_token, api_secret=API_SECRET)
    return sess

# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------
def refresh_if_needed() -> KiteConnect:
    """
    Returns a KiteConnect instance with a valid access_token.
    Order of preference:
      1) cached access_token in tokens.json
      2) renew via cached refresh_token
      3) renew via KITE_REFRESH_TOKEN env var (GitHub Secret)
      4) full headless login (stub)
    """
    kite   = KiteConnect(api_key=API_KEY)
    tokens = _load_tokens()

    # ‼️ NEW — pull refresh_token from environment if not in file
    env_refresh = os.getenv("KITE_REFRESH_TOKEN")
    if env_refresh and not tokens.get("refresh_token"):
        tokens["refresh_token"] = env_refresh

    # 1️⃣ Try cached access_token
    if tokens.get("access_token"):
        kite.set_access_token(tokens["access_token"])
