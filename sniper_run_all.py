from sniper_engine import generate_sniper_trades, save_trades_to_json

print("🚀 Running Sniper System...")

try:
    trades = generate_sniper_trades()
    save_trades_to_json(trades)
    print("✅ Sniper run complete.")
except Exception as e:
    print(f"❌ Sniper run failed: {e}")
