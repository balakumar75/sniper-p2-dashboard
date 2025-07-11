from flask import Flask, render_template
import json
import os

# Import the trade updater logic
from trade_updater import run_trade_updater

app = Flask(__name__)

@app.route('/')
def index():
    # Update the trades before rendering
    run_trade_updater()

    # ✅ Load from root directory (not data/)
    trades_file = "trades.json"
    trades = []

    if os.path.exists(trades_file):
        with open(trades_file, 'r', encoding='utf-8') as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []

    return render_template('index.html', trades=trades)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
