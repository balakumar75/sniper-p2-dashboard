#!/usr/bin/env python3
import json, pathlib, textwrap
from datetime import datetime

ROOT = pathlib.Path(__file__).parent.parent
BEST = ROOT / "best_params.json"
CFG  = ROOT / "config.py"
REP  = ROOT / ".github/scripts/backtest_report.md"

# 1) Patch config.py
best = json.loads(BEST.read_text())
mapping = {
    "RSI_MIN":        best["RSI"],
    "ADX_MIN":        best["ADX"],
    "VOL_MULTIPLIER": best["VOL"],
    "POPCUT":         best["POPCUT"],
    "TOP_N_MOMENTUM": best["MOM"]
}
lines = CFG.read_text().splitlines()
out = []
for L in lines:
    for k,v in mapping.items():
        if L.startswith(f"{k}"):
            L = f"{k} = {v}"
    out.append(L)
CFG.write_text("\n".join(out))

# 2) Write report
report = textwrap.dedent(f"""\
# Weekly Back‑test Report

**Best parameters**  
```json
{json.dumps(best, indent=2)}
