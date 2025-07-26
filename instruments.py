import json
import pathlib
from config import FNO_SYMBOLS

# ── Load spot tokens you just fetched ───────────────────────────────────────
BASE      = pathlib.Path(__file__).parent
SPOT_MAP  = json.loads((BASE / "spot_tokens.json").read_text())

# ── Build your spot map, defaulting to 0 if missing ────────────────────────
SYMBOL_TO_TOKEN = {
    sym: SPOT_MAP.get(sym, 0)
    for sym in FNO_SYMBOLS
}

# ── Load your F&O token JSONs (from previous fetch) ────────────────────────
FUT_DATA = json.loads((BASE / "future_tokens.json").read_text())
PE_DATA  = json.loads((BASE / "option_pe.json").read_text())
CE_DATA  = json.loads((BASE / "option_ce.json").read_text())

# ── Futures tokens by expiry ───────────────────────────────────────────────
FUTURE_TOKENS = {
    sym: {
        "2025-07-31": FUT_DATA.get(sym, 0),
        "2025-08-28": FUT_DATA.get(sym, 0),
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
