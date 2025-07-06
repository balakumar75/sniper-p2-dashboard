# ✅ index_template.py
from datetime import datetime

def render_dashboard(trades):
    now = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    rows = ""
    for t in trades:
        tags = " | ".join(t.get("tags", []))
        rows += f"""
        <tr>
            <td>{t['date']}</td>
            <td>{t['symbol']}</td>
            <td>{t['type']}</td>
            <td>{t['entry']}</td>
            <td>{t['cmp']}</td>
            <td>{t['target']}</td>
            <td>{t['sl']}</td>
            <td>{t['pop']}</td>
            <td>{t['action']}</td>
            <td>{t['sector']}</td>
            <td>{tags}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Sniper Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #121212;
                color: #eee;
                padding: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #555;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #222;
            }}
            tr:nth-child(even) {{
                background-color: #1e1e1e;
            }}
        </style>
    </head>
    <body>
        <h1>Sniper Trade Dashboard</h1>
        <p>📅 Last Refreshed: <strong>{now}</strong></p>
        <table>
            <tr>
                <th>Date</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Entry</th>
                <th>CMP</th>
                <th>Target</th>
                <th>SL</th>
                <th>PoP</th>
                <th>Action</th>
                <th>Sector</th>
                <th>Tags</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
