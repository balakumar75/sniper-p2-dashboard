# ✅ sniper_run_all.py
from templates.index_template import render_dashboard
from trades import SNIPER_TRADES
from datetime import datetime

if __name__ == "__main__":
    print("Running Sniper System...")
    print(f"✅ {len(SNIPER_TRADES)} trades generated.")
    print("🔍 Trade Preview:", SNIPER_TRADES[:1])
    
    now = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
    render_dashboard(SNIPER_TRADES, last_updated=now)
    
    print("✅ index.html updated at dashboard/index.html")
    print("🏁 Sniper run complete.")
