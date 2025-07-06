from flask import Flask, send_file

app = Flask(__name__)

@app.route("/")
def serve_dashboard():
    try:
        return send_file("index.html")
    except Exception as e:
        return f"❌ Error loading dashboard: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
