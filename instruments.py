# instruments.py

import json
import pathlib
from config import FNO_SYMBOLS

# ── Spot tokens (unchanged) ────────────────────────────────────────────────
SYMBOL_TO_TOKEN = {
    "RELIANCE":  738561,
    "TCS":       2953217,
    "HDFCBANK":  341249,
    "INFY":      408065,
    "ICICIBANK": 1270529,
    # … add any remaining spot tokens you need …
}

# ── Load the JSON files you just fetched ────────────────────────────────────
BASE = pathlib.Path(__file__).parent
FUTURE_DATA = json.loads((BASE / "future_tokens.json").read_text())
PE_DATA     = json.loads((BASE / "option_pe.json").read_text())
CE_DATA     = json.loads((BASE / "option_ce.json").read_text())

# ── Futures tokens by expiry────────────────────────────────────────────────
# FUTURE_DATA is a dict: { symbol: token, … }
FUTURE_TOKENS = {
    sym: {
        "2025-07-31": FUTURE_DATA.get(sym, 0),
        "2025-08-28": FUTURE_DATA.get(sym, 0),
    }
    for sym in FNO_SYMBOLS
}

# ── Option tokens by expiry → type → strike → token ────────────────────────
OPTION_TOKENS = {
    sym: {
      "2025-07-31": {
        "PE": PE_DATA.get(sym, {}),
        "CE": CE_DATA.get(sym, {}),
      }
    }
    for sym in FNO_SYMBOLS
}
