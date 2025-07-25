#!/usr/bin/env python3
"""
patch_config.py

Reads best_params.json, updates config.py accordingly,
and writes a backtest_report.md summary.
"""

import json
import re
from pathlib import Path
from datetime import date
import textwrap

# Paths
BEST   = Path("best_params.json")
CONFIG = Path("config.py")
REPORT = Path("backtest_report.md")

# 1) Load best_params.json
if not BEST.exists():
    print("⚠️  best_params.json not found – skipping patch.")
    exit(0)

best = json.loads(BEST.read_text())

# 2) Read and patch config.py
cfg_lines = CONFIG.read_text().splitlines()
mapping   = {
    "RSI_MIN":         best.get("RSI"),
    "ADX_MIN":         best.get("ADX"),
    "VOL_MULTIPLIER":  best.get("VOL"),
    "DONCHIAN_WINDOW": best.get("DC"),
    "N_SIGMA_PRIMARY": best.get("SIGMA"),
}

new_cfg = []
for line in cfg_lines:
    for key, val in mapping.items():
        if re.match(rf"^{key}\s*=", line):
            line = f"{key} = {val}"
    new_cfg.append(line)

CONFIG.write_text("\n".join(new_cfg) + "\n")
print("✅ Updated config.py with best parameters.")

# 3) Write backtest_report.md
report_md = textwrap.dedent(f"""
# Weekly Back-test

**Best combo**

```json
{json.dumps(best, indent=2)}
```

_Auto-generated on {date.today().isoformat()}_
""")

REPORT.write_text(report_md)
print("💾 Wrote backtest_report.md.")
