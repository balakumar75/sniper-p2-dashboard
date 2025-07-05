from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1 style="color:green;">✅ Sniper Dashboard is Working Online!</h1><p>Accessible from mobile now.</p>'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
