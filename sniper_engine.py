import json
import os
from trades import get_all_trades
from datetime import datetime

def run_sniper_system():
    print("📊 Running Sniper System...")

    try:
        trades = get_all_trades()

        print(f"✅ {len(trades)} trades generated." if trades else "⚠️ No trades found.")

        # Save trades.json for visibility
        with open("trades.json", "w", encoding="utf-8") as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)

        # Direct debug HTML (bypassing template)
        html = f"""
        <!DOCTYPE html>
        <html><body style='font-family:Arial; background:#111; color:white; padding:30px'>
        <h1>🧪 Sniper Debug Mode</h1>
        <p><strong>Last Updated:</strong> {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}</p>
        <p><strong>Total Trades:</strong> {len(trades)}</p>
        <ul>
            {''.join(f"<li>{trade['symbol']} — {trade['pop']} — {trade['action']}</li>" for trade in trades)}
        </ul>
        </body></html>
        """

        output_path = os.path.join("dashboard", "index.html")
        os.makedirs("dashboard", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ index.html updated at {output_path}")
        print("🏁 Sniper run complete.")

    except Exception as e:
        print(f"❌ Sniper Engine Error: {e}")
