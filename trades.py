import json
import os
from datetime import datetime
from flask import Blueprint, jsonify
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Load your Kite Connect credentials
load_dotenv()
API_KEY = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

trades_api = Blueprint('trades_api', __name__)
TRADES_FILE = os.path.join(os.path.dirname(__file__), "trades.json")

def fetch_live_price(trade):
    """
    Fetch the latest price for a given trade.
    Falls back to the original CMP if there's an error.
    """
    symbol = trade.get('symbol')
    ttype = trade.get('type', 'Cash').lower()
    # Prefix correctly for NSE vs NFO
    if ttype in ('futures', 'options'):
        instrument = f"NFO:{symbol}"
    else:
        instrument = f"NSE:{symbol}"
    try:
        data = kite.ltp(instrument)
        return data[instrument]['last_price']
    except Exception as e:
        print(f"❌ Error fetching price for {instrument}: {e}")
        return trade.get('cmp')

@trades_api.route("/api/trades", methods=["GET"])
def get_trades():
    try:
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, "r", encoding="utf-8") as f:
                trades = json.load(f)

            # 1) Refresh CMP for all open trades
            for t in trades:
                if t.get('status', 'Open').lower() == 'open':
                    old = t.get('cmp')
                    new = fetch_live_price(t)
                    if new != old:
                        print(f"🔄 Updated CMP for {t['symbol']}: {old} → {new}")
                        t['cmp'] = new

            # 2) Sort by entry date descending
            trades.sort(
                key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
                reverse=True
            )

            # 3) Log count and types
            types = {t.get('type', 'Unknown') for t in trades}
            print(f"✅ Loaded {len(trades)} trades — types: {types}")

            return jsonify(trades), 200
        else:
            print("❌ trades.json not found")
            return jsonify([]), 200

    except Exception as e:
        print(f"❌ Error loading trades.json: {e}")
        return jsonify([]), 500
