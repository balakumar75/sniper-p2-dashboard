import json
import os
from flask import Blueprint, jsonify

TRADES_FILE = "trades.json"

trades_api = Blueprint('trades_api', __name__)

@trades_api.route("/api/trades", methods=["GET"])
def get_trades():
    try:
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, "r", encoding="utf-8") as f:
                trades = json.load(f)
                if isinstance(trades, list):
                    return jsonify(trades), 200  # ✅ Always return 200
                else:
                    print("⚠️ Invalid data format in trades.json")
                    return jsonify([]), 200  # ✅ Safe fallback
        else:
            print("⚠️ trades.json file not found.")
            return jsonify([]), 200  # ✅ Return 200 with empty list
    except Exception as e:
        print(f"❌ Error loading trades.json: {e}")
        return jsonify([]), 500
