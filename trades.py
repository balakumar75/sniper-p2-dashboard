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
                if isinstance(trades, list) and len(trades) > 0:
                    return jsonify(trades)
                else:
                    print("⚠️ trades.json found but contains no trades.")
                    return jsonify([]), 204
        else:
            print("⚠️ trades.json file not found at runtime.")
            return jsonify([]), 404
    except Exception as e:
        print(f"❌ Error loading trades.json: {e}")
        return jsonify([]), 500
