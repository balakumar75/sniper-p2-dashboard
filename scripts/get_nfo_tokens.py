#!/usr/bin/env python3
# scripts/get_nfo_tokens.py

import os, sys, json
from datetime import datetime

# Make repo root importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from token_manager import refresh_if_needed
from config import FNO_SYMBOLS

# 1️⃣ Authenticate
kite = refresh_if_needed()

# 2️⃣ Fetch all NFO instruments
all_nfo = kite.instruments("NFO")

# 3️⃣ Prepare containers
expiry_date = datetime(2025, 7, 31)          # your target expiry
expiry_ts   = expiry_date.strftime("%d%b%Y").upper()  # "31JUL2025"

future_tokens = {sym: 0 for sym in FNO_SYMBOLS}
option_pe     = {sym: {} for sym in FNO_SYMBOLS}
option_ce     = {sym: {} for sym in FNO_SYMBOLS}

# 4️⃣ Populate
for inst in all_nfo:
    ts  = inst["tradingsymbol"]     # e.g. "RELIANCE31JUL2025PE1400"
    tok = inst["instrument_token"]
    for sym in FNO_SYMBOLS:
        # FUTURES: exact match
        if ts == f"{sym}{expiry_ts}":
            future_tokens[sym] = tok
        # OPTIONS: startswith + PE/CE + strike
        if ts.startswith(f"{sym}{expiry_ts}PE"):
            strike = int(ts.split("PE")[-1])
            option_pe[sym][strike] = tok
        if ts.startswith(f"{sym}{expiry_ts}CE"):
            strike = int(ts.split("CE")[-1])
            option_ce[sym][strike] = tok

# 5️⃣ Write out JSON
with open("future_tokens.json","w") as f: json.dump(future_tokens, f, indent=2)
with open("option_pe.json",   "w") as f: json.dump(option_pe,     f, indent=2)
with open("option_ce.json",   "w") as f: json.dump(option_ce,     f, indent=2)

print("✅ Generated future_tokens.json, option_pe.json, option_ce.json")
