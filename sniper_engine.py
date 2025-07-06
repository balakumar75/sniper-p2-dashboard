import json
import os
from trades import get_all_trades
from jinja2 import Template
from datetime import datetime

def run_sniper_system():
    print("📊 Running Sniper System...")

    try:
        trades = get_all_trades()

        if not trades:
            print("⚠️ No trades found.")
        else:
            print(f"✅ {len(trades)} trades generated.")
        
        # ✅ Print trades to verify what is being passed to HTML
        print("🔍 Trade Preview:", json.dumps(trades, indent=2))

        # Save trades.json for reference
        with open("trades.json", "w", encoding="utf-8") as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)

        # Load and render the template
        template_path = os.path.join("templates", "index_template.html")
        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        html = template.render(
            trades=trades,
            updated=datetime.now().strftime('%d %b %Y, %I:%M:%S %p')
        )

        # Save to dashboard/index.html
        output_path = os.path.join("dashboard", "index.html")
        os.makedirs("dashboard", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ index.html updated at {output_path}")
        print("🏁 Sniper run complete.")

    except Exception as e:
        print(f"❌ Sniper Engine Error: {e}")
