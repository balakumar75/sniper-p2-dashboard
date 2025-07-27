#!/usr/bin/env python3
# scripts/get_nfo_tokens.py

import os
import sys
import json
from datetime import date

# ── Make repo root importable ────────────────────────────────────────────────
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

import kite_patch                  # patch KiteConnect host
from token_manager import refresh_if_needed
from config import FNO_SYMBOLS

# 1️⃣ Authenticate
kite = refresh_if_needed()

# 2️⃣ Download all NFO instruments
all_nfo = kite.instruments("NFO")

# 3️⃣ Set your target expiry
expiry_date = date(2025, 7, 31)      # adjust if you need a different expiry

# 4️⃣ Prepare containers
future_tokens = { sym: 0 for sym in FNO_SYMBOLS }
option_pe     = { sym: {} for sym in FNO_SYMBOLS }
option_ce     = { sym: {} for sym in FNO_SYMBOLS }

# 5️⃣ Populate using each instrument’s fields
for inst in all_nfo:
    sym    = inst.get("name")            # underlying, e.g. "RELIANCE"
    exp    = inst.get("expiry")          # a datetime.date
    itype  = inst.get("instrument_type") # "FUT", "PE", or "CE"
    tok    = inst.get("instrument_token")
    strike = inst.get("strike")          # float or int

    # only our universe & chosen expiry
    if sym not in FNO_SYMBOLS or exp != expiry_date:
        continue

    if itype == "FUT":
        future_tokens[sym] = tok

    elif itype == "PE" and strike is not None:
        option_pe[sym][int(strike)] = tok

    elif itype == "CE" and strike is not None:
        option_ce[sym][int(strike)] = tok

# 6️⃣ Write JSON artifacts
with open("future_tokens.json", "w") as f:
    json.dump(future_tokens, f, indent=2)
with open("option_pe.json", "w") as f:
    json.dump(option_pe, f, indent=2)
with open("option_ce.json", "w") as f:
    json.dump(option_ce, f, indent=2)

print("✅ Generated future_tokens.json, option_pe.json, option_ce.json")
