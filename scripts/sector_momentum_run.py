#!/usr/bin/env python
"""
Run sector momentum after authenticating Kite and injecting into utils.
"""

import kite_patch
from token_manager import refresh_if_needed
import utils
from sector_momentum import compute_sector_momentum

# 1) Auth & inject
kite = refresh_if_needed()
utils.set_kite(kite)

# 2) Compute & print heatmap
df = compute_sector_momentum()
print(df.to_markdown(index=False))
