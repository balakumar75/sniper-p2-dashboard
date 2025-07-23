import os, json
from kiteconnect import KiteConnect, exceptions

TOKENS_FILE = "tokens.json"
API_KEY     = os.getenv("KITE_API_KEY")
API_SECRET  = os.getenv("KITE_API_SECRET")


# ------------------------------------------------------------------ helpers
def _load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------- headless
def _headless_login(kite: KiteConnect):
    raise RuntimeError("Headless login not implemented")


# --------------------------------------------------------- main entry-point
def refresh_if_needed() -> KiteConnect:
    """
    Returns a KiteConnect instance with a valid access_token.
    Order:
      1. cached access_token          (tokens.json)
      2. renew via cached refresh_token
      3. renew via env var KITE_REFRESH_TOKEN  ← NEW
      4. fall back to headless login  (stub)
    """
    kite   = KiteConnect(api_key=API_KEY)
    tokens = _load_tokens()

    # NEW: take refresh_token from GitHub Secret if file is empty
    env_refresh = os.getenv("KITE_REFRESH_TOKEN")
    if env_refresh and not tokens.get("refresh_token"):
        tokens["refresh_token"] = env_refresh

    # 1️⃣ reuse existing access_token
    if tokens.get("access_token"):
        kite.set_access_token(tokens["access_token"])
        try:
            kite.profile()             # cheap ping
            return kite
        except exceptions.TokenException:
            pass                       # expired → keep going

    # 2️⃣ renew via refresh_token
    if tokens.get("refresh_token"):
        try:
            sess = kite.renew_access_token(
                tokens["refresh_token"], api_secret=API_SECRET)
            _save_tokens(sess)
            return kite                # ← **THIS was missing**
        except exceptions.TokenException:
            pass                       # invalid / revoked → keep going

    # 3️⃣ full login fallback
    sess = _headless_login(kite)
    _save_tokens(sess)
    return kite
