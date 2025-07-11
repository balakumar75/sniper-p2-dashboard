import json
import os
from flask import Blueprint, jsonify

trades_api = Blueprint('trades_api', __name__)
TRADES_FILE = os.path.join(os.path.dirname(__file__), "trades.json")

@trades_api.route("/api/trades", methods=["GET"])
def get_trades():
    try:
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, "r", encoding="utf-8") as f:
                trades = json.load(f)
                print(f"✅ Loaded {len(trades)} trades")
                return jsonify(trades), 200
        else:
            print("❌ trades.json not found")
            return jsonify([]), 200
    except Exception as e:
        print(f"❌ Error loading trades.json: {e}")
        return jsonify([]), 500
