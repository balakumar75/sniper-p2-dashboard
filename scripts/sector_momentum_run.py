#!/usr/bin/env python
"""
Run sector momentum after authenticating Kite and injecting into utils.
"""

import sys
import pathlib

# ── 0) Make sure we can import root‑level modules (kite_patch, utils, etc.) ──
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ── 1) Import & auth ───────────────────────────────────────────────────────
import kite_patch              # your rate‑limit patches; must come before KiteConnect
from token_manager import refresh_if_needed
import utils                   # now resolvable thanks to sys.path above
from sector_momentum import compute_sector_momentum

# 2) Authenticate & inject into utils
kite = refresh_if_needed()
utils.set_kite(kite)

# 3) Compute sector momentum & print a markdown table
df = compute_sector_momentum()
print(df.to_markdown(index=False))
