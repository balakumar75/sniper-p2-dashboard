#!/usr/bin/env python3
# scripts/get_nfo_tokens.py

import os
import sys
import json
from datetime import date

# ── Make repo root importable ────────────────────────────────────────────────
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

import kite_patch                   # ensure KiteConnect uses your patched host
from token_manager import refresh_if_needed
from config import FNO_SYMBOLS

# 1️⃣ Authenticate
kite = refresh_if_needed()

# 2️⃣ Download all NFO instruments
all_nfo = kite.instruments("NFO")

# 3️⃣ Prepare containers for a single expiry
expiry_date = date(2025, 7, 31)     # adjust if you need a different expiry

future_tokens = { sym: 0 for sym in FNO_SYMBOLS }
option_pe     = { sym: {} for sym in FNO_SYMBOLS }
option_ce     = { sym: {} for sym in FNO_SYMBOLS }

# Sort symbols by length so longer names (e.g. BHARTIARTL) match before shorter (e.g. ITC)
syms_sorted = sorted(FNO_SYMBOLS, key=lambda s: len(s), reverse=True)

# 4️⃣ Populate by inspecting each instrument’s fields
for inst in all_nfo:
    ts       = inst.get("tradingsymbol", "")
    inst_type= inst.get("instrument_type")
    exp      = inst.get("expiry")         # a datetime.date
    tok      = inst.get("instrument_token")
    strike   = inst.get("strike")         # float or int

    # skip different expiries
    if exp != expiry_date:
        continue

    # find which underlying symbol this belongs to
    sym = next((s for s in syms_sorted if ts.startswith(s)), None)
    if not sym:
        continue

    if inst_type == "FUT":
        future_tokens[sym] = tok

    elif inst_type == "PE" and strike is not None:
        option_pe[sym][int(strike)] = tok

    elif inst_type == "CE" and strike is not None:
        option_ce[sym][int(strike)] = tok

# 5️⃣ Write out JSON for easy copy–paste into instruments.py
with open("future_tokens.json", "w") as f:
    json.dump(future_tokens, f, indent=2)
with open("option_pe.json", "w") as f:
    json.dump(option_pe, f, indent=2)
with open("option_ce.json", "w") as f:
    json.dump(option_ce, f, indent=2)

print("✅ Generated future_tokens.json, option_pe.json, option_ce.json")
