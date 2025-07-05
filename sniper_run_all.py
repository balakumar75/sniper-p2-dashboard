print("✅ Starting sniper_run_all.py")

from sniper_engine import run_sniper_system

def main():
    print("🚀 Running Sniper Engine...")
    try:
        run_sniper_system()
        print("✅ Sniper Engine Completed Successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
