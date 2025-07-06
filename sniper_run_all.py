from flask import Flask, send_file
import subprocess

app = Flask(__name__)

@app.route('/')
def serve_dashboard():
    # Force-refresh dashboard before serving
    subprocess.run(["python", "sniper_run_all.py"])
    return send_file('dashboard/index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
