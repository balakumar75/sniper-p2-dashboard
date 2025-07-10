import json
from datetime import datetime
from fno_stocks import get_fno_stocks
from utils import fetch_cmp, validate_structure, calculate_pop, get_sector, detect_tags

TRADES_FILE = "trades.json"

def generate_sniper_trades():
    print("🚀 Sniper Engine Starting...")

    try:
        symbols = get_fno_stocks()
        print(f"📈 Loaded {len(symbols)} F&O stocks")
    except Exception as e:
        print(f"❌ Error loading F&O stocks: {e}")
        return []

    valid_trades = []

    for symbol in symbols:
        try:
            print(f"🔍 Processing {symbol}...")

            cmp = fetch_cmp(symbol)
            if cmp is None:
                print(f"⚠️ Skipping {symbol} — CMP not found")
                continue

            structure_ok = validate_structure(symbol)
            if not structure_ok:
                print(f"⚠️ Skipping {symbol} — Structure not valid")
                continue

            pop = calculate_pop(symbol)
            sector = get_sector(symbol)
            tags = detect_tags(symbol)

            entry = round(cmp, 2)
            target = round(entry * 1.02, 2)   # Exampl*
