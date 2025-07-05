from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1 style="color:green;">✅ Sniper Dashboard is Working Locally!</h1><p>You can now deploy to Render.</p>'

if __name__ == '__main__':
    app.run(debug=True)
