#!/usr/bin/env python3
# scripts/get_nfo_tokens.py

import os
import sys
import json

# ── Add repo root to path so we can import token_manager & config ─────────────
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from token_manager import refresh_if_needed
from config import FNO_SYMBOLS

# 1) Authenticate
kite = refresh_if_needed()

# 2) Fetch all NFO instruments
all_nfo = kite.instruments("NFO")

# 3) Prepare containers
expiry      = "2025-07-31"             # adjust if needed
expiry_str  = expiry.replace("-", "")  # "20250731"

future_tokens = {sym: 0 for sym in FNO_SYMBOLS}
option_pe     = {sym: {} for sym in FNO_SYMBOLS}
option_ce     = {sym: {} for sym in FNO_SYMBOLS}

# 4) Populate futures & options
for inst in all_nfo:
    ts  = inst["tradingsymbol"]     # e.g. "RELIANCE31JUL2025PE1400"
    tok = inst["instrument_token"]

    # FUTURES
    for sym in FNO_SYMBOLS:
        if ts == f"{sym}{expiry_str}":
            future_tokens[sym] = tok

    # OPTIONS: PE / CE
    for sym in FNO_SYMBOLS:
        if ts.startswith(f"{sym}{expiry_str}PE"):
            strike = int(ts.split("PE")[-1])
            option_pe[sym][strike] = tok
        if ts.startswith(f"{sym}{expiry_str}CE"):
            strike = int(ts.split("CE")[-1])
            option_ce[sym][strike] = tok

# 5) Write JSON files
with open("future_tokens.json", "w") as f:
    json.dump(future_tokens, f, indent=2)
with open("option_pe.json", "w") as f:
    json.dump(option_pe, f, indent=2)
with open("option_ce.json", "w") as f:
    json.dump(option_ce, f, indent=2)

print("✅ Generated future_tokens.json, option_pe.json, option_ce.json")
