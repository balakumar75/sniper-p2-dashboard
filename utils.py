import requests
import json
import os
import random

# ✅ Load access token from token.txt or environment variable
def load_access_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            return f.read().strip()
    return os.environ.get("ZERODHA_ACCESS_TOKEN", "")

# ✅ Fetch CMP from Zerodha Kite API
def fetch_cmp(symbol):
    access_token = load_access_token()
    api_key = os.environ.get("ZERODHA_API_KEY", "")
    headers = {
        "Authorization": f"token {api_key}:{access_token}"
    }

    symbol_map = {
        "NSE": "NSE:",
        "BSE": "BSE:",
        "NFO": "NFO:"
    }

    if symbol.endswith("FUT"):
        exchange = "NFO"
    else:
        exchange = "NSE"

    try:
        full_symbol = f"{exchange}:{symbol}"
        url = f"https://api.kite.trade/quote?i={full_symbol}"
        response = requests.get(url, headers=headers)
        data = response.json
