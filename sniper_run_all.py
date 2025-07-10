from sniper_engine import generate_sniper_trades, save_trades_to_json

print("🚀 Sniper Engine Starting...")

try:
    trades = generate_sniper_trades()
    print(f"✅ Trades generated: {len(trades)}")

    if len(trades) > 0:
        print("🔍 Preview of 1st trade:", trades[0])
    else:
        print("⚠️ No trades generated. Check sniper filters or logic.")

    save_trades_to_json(trades)
    print("✅ trades.json saved successfully.")
except Exception as e:
    print("❌ Error during Sniper Engine run:", e)

print("✅ Sniper run complete.")
