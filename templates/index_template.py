import datetime
import os

def render_dashboard(trades):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sniper Dashboard</title>
    <style>
        body {{
            font-family: Arial; background: #0f0f0f; color: #ffffff; padding: 20px;
        }}
        h1 {{
            color: #00ff88;
        }}
        .tag {{
            padding: 4px 6px; margin: 2px; background: #1e1e1e; border-radius: 5px; display: inline-block;
        }}
        table {{
            width: 100%; border-collapse: collapse; margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #444; padding: 8px; text-align: left;
        }}
        th {{
            background-color: #1f1f1f; color: #00ff88;
        }}
        select {{
            padding: 6px; background: #1f1f1f; color: #00ff88; border: 1px solid #00ff88; margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>🎯 Sniper Trade Dashboard</h1>
    <p><strong>Last Refreshed:</strong> {datetime.datetime.now().strftime("%d %b %Y, %I:%M:%S %p")}</p>

    <label for="statusFilter"><strong>Filter by Status:</strong></label>
    <select id="statusFilter">
        <option value="All">All</option>
        <option value="Open">Open</option>
        <option value="Target Hit">Target Hit</option>
        <option value="SL Hit">SL Hit</option>
    </select>

    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Entry</th>
                <th>CMP</th>
                <th>Target</th>
                <th>SL</th>
                <th>Status</th>
                <th>PoP</th>
                <th>Action</th>
                <th>Sector</th>
                <th>Tags</th>
            </tr>
        </thead>
        <tbody>
    """
    for trade in trades:
        tags_html = ''.join(f'<span class="tag">{tag}</span>' for tag in trade['tags'])
        html += f"""
        <tr data-status="{trade['status']}">
            <td>{trade['date']}</td>
            <td>{trade['symbol']}</td>
            <td>{trade['type']}</td>
            <td>{trade['entry']}</td>
            <td>{trade['cmp']}</td>
            <td>{trade['target']}</td>
            <td>{trade['sl']}</td>
            <td>{trade['status']}</td>
            <td>{trade['pop']}</td>
            <td>{trade['action']}</td>
            <td>{trade['sector']}</td>
            <td>{tags_html}</td>
        </tr>
        """
    html += """
        </tbody>
    </table>

    <script>
        document.getElementById("statusFilter").addEventListener("change", function () {
            const selected = this.value;
            const rows = document.querySelectorAll("tbody tr");

            rows.forEach(row => {
                if (selected === "All" || row.dataset.status === selected) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    </script>
</body>
</html>"""

    os.makedirs("dashboard", exist_ok=True)
    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
