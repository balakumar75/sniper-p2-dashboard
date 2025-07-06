from flask import Flask, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def serve_dashboard():
    try:
        subprocess.run(["python", "sniper_run_all.py"], check=True)
    except Exception as e:
        return f"Error running sniper_run_all.py: {e}"

    path = os.path.join("dashboard", "index.html")
    if os.path.exists(path):
        return send_file(path)
    else:
        return "Dashboard file not found. Please run sniper_run_all.py manually."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
