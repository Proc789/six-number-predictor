from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, this is the 6-number predictor app!"

if __name__ == "__main__":
    app.run()
