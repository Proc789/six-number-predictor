from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
      <head>
        <title>6 號碼預測器</title>
      </head>
      <body style="text-align: center; padding-top: 100px;">
        <h1>6 號碼預測器</h1>
        <button onclick="alert('預測號碼：1, 2, 3, 4, 5, 6')">產生號碼</button>
      </body>
    </html>
    """)

if __name__ == "__main__":
    app.run()
