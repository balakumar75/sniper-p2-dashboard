import datetime
import os

def render_dashboard(trades):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sniper Dashboard</title>
    <style>
        body {{ font-family: Arial; background: #0f0f0f; color: #ffffff; padding: 20px; }}
        h1 {{ color: #00ff88; }}
        .tag {{ padding: 4px 6px; margin: 2px; background: #1e1e1e; border-radius: 5px; display: inline-block; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
        th {{ background-color: #1f1f1f; color: #00ff88; }}
        select {{ margin-bottom: 10px; padding: 5px; }}
    </style>
    <script>
        function filterStatus() {{
            var selected = document.getElementById("statusFilter").value.toLowerCase();
            var rows = document.querySelectorAll("tbody tr");
            rows.forEach(row => {{
                var status = row.getAttribute("data-status").toLowerCase();
                row.style.display = (selected === "all" || status === selected) ? "" : "none";
            }});
        }}
    </script>
</head>
<body>
    <h1>🎯 Sniper Trade Dashboard</h1>
    <p><strong>Last Refreshed:</strong> {datetime.datetime.now().strftime("%d %b %Y, %I:%M:%S %p")}</p>
    <label for="statusFilter">🔍 Filter by Status:</label>
    <select id="statusFilter" onchange="filterStatus()">
        <option value="all">All</option>
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
        tags_html = ''.join(f'<span class="tag">{tag}</span>' for tag in trade.get('tags', []))
        status = trade.get("status", "Open")
        html += f"""
        <tr data-status="{status}">
            <td>{trade.get('date', '')}</td>
            <td>{trade.get('symbol', '')}</td>
            <td>{trade.get('type', '')}</td>
            <td>{trade.get('entry', '')}</td>
            <td>{trade.get('cmp', '')}</td>
            <td>{trade.get('target', '')}</td>
            <td>{trade.get('sl', '')}</td>
            <td>{status}</td>
            <td>{trade.get('pop', '')}</td>
            <td>{trade.get('action', '')}</td>
            <td>{trade.get('sector', '')}</td>
            <td>{tags_html}</td>
        </tr>
        """
    html += """
        </tbody>
    </table>
</body>
</html>"""

    os.makedirs("dashboard", exist_ok=True)
    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
