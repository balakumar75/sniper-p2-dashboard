from sniper_engine import generate_sniper_trades, save_trades_to_json

print("🚀 Running Sniper System...")

trades = generate_sniper_trades()
save_trades_to_json(trades)

print("✅ All done.")
