#!/usr/bin/env python3
# scripts/get_nfo_tokens.py

import os
import sys

# ── Ensure repo root is on PYTHONPATH ────────────────────────────────────────
# This lets us import token_manager, utils, config, etc.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

import json
from token_manager import refresh_if_needed
import utils
from config import FNO_SYMBOLS

# 1) Authenticate & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Download all NFO instruments
all_nfo = kite.instruments("NFO")

# 3) Build your mappings for a given expiry
expiry = "2025-07-31"              # change if needed
expiry_str = expiry.replace("-", "")  # "20250731"

future_tokens = {}
option_pe   = {}
option_ce   = {}

# Initialize empty entries
for sym in FNO_SYMBOLS:
    future_tokens[sym] = 0
    option_pe[sym]     = {}
    option_ce[sym]     = {}

# Populate from instrument list
for inst in all_nfo:
    ts  = inst["tradingsymbol"]     # e.g. "RELIANCE31JUL2025PE1400"
    tok = inst["instrument_token"]
    
    # FUTURES
    for sym in FNO_SYMBOLS:
        if ts == f"{sym}{expiry_str}":
            future_tokens[sym] = tok
    
    # OPTIONS: PE and CE
    for sym in FNO_SYMBOLS:
        if ts.startswith(f"{sym}{expiry_str}PE"):
            strike = int(ts.split("PE")[-1])
            option_pe[sym][strike] = tok
        if ts.startswith(f"{sym}{expiry_str}CE"):
            strike = int(ts.split("CE")[-1])
            option_ce[sym][strike] = tok

# 4) Write out JSON for manual copy‑paste
with open("future_tokens.json", "w") as f:
    json.dump(future_tokens, f, indent=2)
with open("option_pe.json", "w") as f:
    json.dump(option_pe, f, indent=2)
with open("option_ce.json", "w") as f:
    json.dump(option_ce, f, indent=2)

print("✅ Generated future_tokens.json, option_pe.json, option_ce.json")
