import json
from trades import get_all_trades
from jinja2 import Template
from datetime import datetime

def run_sniper_system():
    print("📊 Running Sniper System...")

    trades = get_all_trades()

    if not trades:
        print("⚠️ No trades found.")
    else:
        print(f"✅ {len(trades)} trades generated.")

    # Save trades.json
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)
        print("✅ trades.json saved.")

    # Load HTML template
    with open("templates/index_template.html", "r") as f:
        template = Template(f.read())

    # Render and write index.html
    html = template.render(trades=trades, updated=datetime.now().strftime('%d %b %Y – %I:%M %p'))
    with open("index.html", "w") as f:
        f.write(html)
        print("✅ index.html updated.")

    print("🏁 Sniper run complete.")
