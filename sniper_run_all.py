from sniper_engine import generate_sniper_trades, save_trades_to_json

def main():
    try:
        print("✅ Starting sniper_run_all.py")
        trades = generate_sniper_trades()

        if trades and isinstance(trades, list):
            save_trades_to_json(trades)
        else:
            print("⚠️ No trades generated or unexpected result format.")
    except Exception as e:
        print(f"❌ ERROR in sniper_run_all.py: {e}")

if __name__ == "__main__":
    main()
