from flask import Flask, render_template
from trades import trades_api
from trade_updater import run_trade_updater

app = Flask(__name__)
app.register_blueprint(trades_api)

@app.route("/")
def index():
    run_trade_updater()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0
