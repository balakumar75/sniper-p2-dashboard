import json
import os
from trades import get_all_trades
from jinja2 import Template
from datetime import datetime

def run_sniper_system():
    print("📊 Running Sniper System...")

    try:
        # Step 1: Get trades
        trades = get_all_trades()

        if not trades:
            print("⚠️ No trades found.")
        else:
            print(f"✅ {len(trades)} trades generated.")

        print("🔍 Trade Preview:\n", json.dumps(trades, indent=2))

        # Step 2: Save trades.json for debugging
        with open("trades.json", "w", encoding="utf-8") as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)

        # Step 3: Load the Jinja template
        template_path = os.path.join("templates", "index_template.html")
        if not os.path.exists(template_path):
            print(f"❌ Template missing: {template_path}")
            return

        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        # Step 4: Render HTML with trades and timestamp
        html = template.render(
            trades=trades,
            updated=datetime.now().strftime('%d %b %Y, %I:%M:%S %p')
        )

        # Step 5: Ensure dashboard folder exists and write index.html
        output_dir = os.path.join(os.getcwd(), "dashboard")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "index.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ index.html rendered to: {output_path}")
        print("🏁 Sniper run complete.")

    except Exception as e:
        print(f"❌ Sniper Engine Error: {e}")
