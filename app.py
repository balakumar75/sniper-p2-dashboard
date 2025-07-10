from flask import Flask, render_template
from trades import trades_api  # ✅ Import the API blueprint
from trade_updater import run_trade_updater  # ✅ Optional updater logic

app = Flask(__name__)
app.register_blueprint(trades_api)  # ✅ Register API route

@app.route("/")
def index():
    run_trade_updater()  # ✅ Update trades if needed
    return render_template("index.html")  # No need to pass trades manually

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
