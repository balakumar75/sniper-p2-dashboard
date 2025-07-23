import os, json, datetime
from kiteconnect import KiteConnect, exceptions

TOKENS_FILE = "tokens.json"
API_KEY     = os.getenv("KITE_API_KEY")
API_SECRET  = os.getenv("KITE_API_SECRET")

def _load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── optional headless login (stub) ─────────────────────────────────────────
def _headless_login(kite):
    """
    If refresh_token is absent/invalid, fall back to automated login.
    Replace `fetch_request_token_somehow()` with your Selenium / PyOTP flow.
    """
    def fetch_request_token_somehow():
        raise RuntimeError("Headless login not implemented")
    req_token = fetch_request_token_somehow()
    sess = kite.generate_session(req_token, api_secret=API_SECRET)
    return sess

# ── public helper ──────────────────────────────────────────────────────────
def refresh_if_needed() -> KiteConnect:
    kite   = KiteConnect(api_key=API_KEY)
    tokens = _load_tokens()

    # 1️⃣ Try cached access_token
    if tokens.get("access_token"):
        kite.set_access_token(tokens["access_token"])
        try:
            kite.profile()          # ping
            return kite
        except exceptions.TokenException:
            pass  # expired

    # 2️⃣ Refresh via refresh_token
    if tokens.get("refresh_token"):
        try:
            new_sess = kite.renew_access_token(
                tokens["refresh_token"], api_secret=API_SECRET)
            _save_tokens(new_sess)
            return kite
        except exceptions.TokenException:
            pass  # refresh_token invalid

    # 3️⃣ Full login fallback
    new_sess = _headless_login(kite)
    _save_tokens(new_sess)
    return kite
