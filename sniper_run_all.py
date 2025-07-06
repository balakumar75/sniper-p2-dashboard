# ✅ sniper_run_all.py
from templates.index_template import render_dashboard
from trades import SNIPER_TRADES

def determine_status(trade):
    cmp = trade["cmp"]
    target = trade["target"]
    sl = trade["sl"]

    if cmp >= target:
        return "🎯 Target Hit"
    elif cmp <= sl:
        return "🛑 SL Hit"
    else:
        return "📈 Open"

if __name__ == "__main__":
    print("Running Sniper System...")
    
    # Assign status dynamically
    for trade in SNIPER_TRADES:
        trade["status"] = determine_status(trade)

    print(f"✅ {len(SNIPER_TRADES)} trades generated.")
    print("🔍 Trade Preview:", SNIPER_TRADES[:1])

    render_dashboard(SNIPER_TRADES)

    print("✅ index.html updated at dashboard/index.html")
    print("🏁 Sniper run complete.")
