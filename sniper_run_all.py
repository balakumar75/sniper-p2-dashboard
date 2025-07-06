import json
from datetime import datetime
from jinja2 import Template

# Load trade data from trades.py
from trades import SNIPER_TRADES

# Sort trades by date (descending)
sorted_trades = sorted(SNIPER_TRADES, key=lambda x: x['date'], reverse=True)

# Load HTML template
with open("templates/index_template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())

# Render the template with the sorted trade data
rendered_html = template.render(
    last_updated=datetime.now().strftime("%d %b %Y, %I:%M:%S %p"),
    trades=sorted_trades
)

# Save the rendered HTML to the dashboard
with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(rendered_html)

print("✅ index.html updated at dashboard/index.html")
print("🏁 Sniper run complete.")
