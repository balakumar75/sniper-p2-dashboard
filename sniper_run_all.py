print("✅ Starting sniper_run_all.py")

from sniper_engine import run_sniper_system  # This should be your core engine
from sniper_utils import load_env  # Optional: if you use .env loading

def main():
    print("🚀 Running Sniper Engine...")
    try:
        run_sniper_system()  # Runs the full sniper scan and dashboard/Telegram update
        print("✅ Sniper Engine Completed Successfully")
    except Exception as e:
        print(f"❌ Error running sniper engine: {e}")

if __name__ == "__main__":
    main()
