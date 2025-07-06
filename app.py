from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/")
def serve_dashboard():
    try:
        dashboard_path = os.path.join("dashboard", "index.html")
        return send_file(dashboard_path)
    except Exception as e:
        return f"❌ Error loading dashboard: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
