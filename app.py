from flask import Flask, render_template
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Load trades
    trades_file = 'data/trades.json'
    trades = []

    if os.path.exists(trades_file):
        with open(trades_file, 'r') as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []

    return render_template('index.html', trades=trades)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
