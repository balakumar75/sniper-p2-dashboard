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

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def refresh_if_needed() -> KiteConnect:
    kite = KiteConnect(api_key=API_KEY)

    # 0️⃣  Daily ACCESS_TOKEN provided as GitHub Secret
    env_access = os.getenv("KITE_ACCESS_TOKEN")
    if env_access:
        kite.set_access_token(env_access)
        try:
            kite.profile()                     # ping – succeeds if token fresh
            return kite                        # ✅ done
        except exceptions.TokenException:
            raise RuntimeError(
                "KITE_ACCESS_TOKEN has expired. "
                "Generate a new one and update the secret."
            )

    # 1️⃣  Fallback to cached tokens.json (optional)
    tokens = _load_tokens()
    if tokens.get("access_token"):
        kite.set_access_token(tokens["access_token"])
        try:
            kite.profile()
            return kite
        except exceptions.TokenException:
            pass  # expired

    raise RuntimeError(
        "No valid KITE_ACCESS_TOKEN supplied and cached token is invalid."
    )
