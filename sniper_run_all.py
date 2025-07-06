from trades import save_trade
from utils.sniper_utils import generate_sniper_trade
import os

if not os.path.exists("dashboard"):
    os.makedirs("dashboard")

print("Running Sniper System...")

# 🔄 Generate trades (from latest sniper engine)
trades = generate_sniper_trade()
print(f"✅ {len(trades)} trades generated.")

for trade in trades:
    print("🔍 Trade Preview:", trade)
    save_trade(trade)

# ✅ Save latest dashboard
with open("templates/index_template.html", "r") as f:
    template = f.read()

table_rows = ""
for trade in trades:
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in trade["tags"]])
    row = f"""
    <tr>
        <td>{trade["date"]}</td>
        <td>{trade["symbol"]}</td>
        <td>{trade["type"]}</td>
        <td>{trade["entry"]}</td>
        <td>{trade["cmp"]}</td>
        <td>{trade["target"]}</td>
        <td>{trade["sl"]}</td>
        <td>{trade["pop"]}</td>
        <td>{trade["action"]}</td>
        <td>{trade["sector"]}</td>
        <td>{tags_html}</td>
    </tr>
    """
    table_rows += row

html_output = template.replace("{{ trade_rows }}", table_rows)
html_output = html_output.replace("{{ last_updated }}", os.popen("date").read().strip())

with open("dashboard/index.html", "w") as f:
    f.write(html_output)

print("✅ index.html updated at dashboard\\index.html")
print("🏁 Sniper run complete.")
