# ✅ sniper_run_all.py
from templates.index_template import render_dashboard
from trades import SNIPER_TRADES

if __name__ == "__main__":
    print("🔁 Running Sniper System...")
    print(f"✅ {len(SNIPER_TRADES)} trades generated.")
    print("🔍 Trade Preview:", SNIPER_TRADES[:1])  # Print one for verification

    print("🛠️ Running dashboard render from correct template path...")
    render_dashboard(SNIPER_TRADES)

    print("✅ index.html updated at dashboard/index.html")
    print("🏁 Sniper run complete.")
