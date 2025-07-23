import os, json
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


# ───────────────────────────────────────────────────────────────────────────
def refresh_if_needed() -> KiteConnect:
    """Return KiteConnect with a *valid* access_token.

    Priority:
      0. KITE_ACCESS_TOKEN (daily secret)  ← you paste this each day
      1. Cached access_token in tokens.json
    """
    kite = KiteConnect(api_key=API_KEY)

    # 0️⃣  daily secret
    env_access = os.getenv("KITE_ACCESS_TOKEN")
    if env_access:
        kite.set_access_token(env_access)
        try:
            kite.profile()
            return kite
        except exceptions.TokenException:
            raise RuntimeError(
                "KITE_ACCESS_TOKEN has expired – paste today’s token in Secrets."
            )

    # 1️⃣  cached file token
    tokens = _load_tokens()
    if tokens.get("access_token"):
        kite.set_access_token(tokens["access_token"])
        try:
            kite.profile()
            return kite
        except exceptions.TokenException:
            pass   # expired

    raise RuntimeError(
        "No valid access token. Paste KITE_ACCESS_TOKEN in GitHub Secrets."
    )
