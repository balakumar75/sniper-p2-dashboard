from flask import Flask, send_file
from sniper_run_all import *  # Ensures dashboard is generated on server start

app = Flask(__name__)

@app.route('/')
def serve_dashboard():
    return send_file('dashboard/index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
