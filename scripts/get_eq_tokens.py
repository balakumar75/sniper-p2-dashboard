#!/usr/bin/env python3
# scripts/get_eq_tokens.py

import os, sys, json

# Make your repo root importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from token_manager import refresh_if_needed
from config import NSE100

# 1️⃣ Authenticate
kite = refresh_if_needed()

# 2️⃣ Pull all NSE instruments
all_nse = kite.instruments("NSE")

# 3️⃣ Build a map for your NSE100 list
spot_tokens = {}
for inst in all_nse:
    ts = inst["tradingsymbol"]   # e.g. "RELIANCE"
    if ts in NSE100:
        spot_tokens[ts] = inst["instrument_token"]

# 4️⃣ Write out spot_tokens.json
with open("spot_tokens.json","w") as f:
    json.dump(spot_tokens, f, indent=2)

print("✅ Generated spot_tokens.json")
