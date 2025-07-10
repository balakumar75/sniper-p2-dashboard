import json
import datetime
from utils import fetch_cmp, validate_structure, calculate_pop, get_sector, detect_tags
from fno_stocks import FNO_LIST  # List of NSE F&O stocks

def run_sniper_engine():
    print("🚀 Starting Sniper Engine...\n")
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    valid_trades = []
    failed_symbols = []

    for symbol in FNO_LIST:
        print(f"🔍 Processing: {symbol}")
        try:
            cmp = fetch_cmp(symbol)
            if cmp is None:
                print(f"❌ Could not fetch CMP for {symbol}")
                failed_symbols.append(symbol)
                continue

            # Validate technical structure (RSI, MACD, Volume, ADX, etc.)
            structure_ok, structure_data = validate_structure(symbol)
            if not structure_ok:
                print(f"⚠️ Structure failed for {symbol}")
                continue

            # Calculate target, SL, PoP%
            entry = cmp
            target = round(cmp * 1.02, 2)
            sl = round(cmp * 0.975, 2)
            pop = calculate_pop(symbol, entry, target, sl)
            sector = get_sector(symbol)
            tags = detect_tags(symbol, structure_data)

            trade = {
                "date": today,
                "symbol": symbol,
                "type": "Cash",  # default, override if Futures/Options
                "entry": entry,
                "cmp": cmp,
                "target": target,
                "sl": sl,
                "pop": f"{pop}%",
                "action": "Buy",
                "sector": sector,
                "tags": tags,
                "status": "Open"
            }

            valid_trades.append(trade)
            print(f"✅ Trade generated: {symbol} @ {cmp}")

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            failed_symbols.append(symbol)

    print(f"\n📊 Total Valid Trades: {len(valid_trades)}")
    print(f"❌ Failed Symbols: {failed_symbols}")

    try:
        with open("trades.json", "w", encoding="utf-8") as f:
            json.dump(valid_trades, f, indent=2)
        print(f"✅ Saved {len(valid_trades)} trades to trades.json")
    except Exception as e:
        print(f"❌ Error saving trades.json: {e}")

    print("✅ Sniper run complete.\n")

if __name__ == "__main__":
    run_sniper_engine()
