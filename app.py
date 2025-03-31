from flask import Flask, render_template_string, request

app = Flask(__name__)

history = []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # 從表單取得用戶輸入的號碼
        numbers = request.form.get("numbers").split(",")
        if len(numbers) == 3:
            # 轉換為整數並儲存
            numbers = list(map(int, numbers))
            history.append(numbers)
            prediction = generate_prediction()
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                  <head>
                    <title>6 號碼預測器</title>
                  </head>
                  <body style="text-align: center; padding-top: 100px;">
                    <h1>6 號碼預測器</h1>
                    <form method="POST">
                        <input type="text" name="numbers" placeholder="輸入三個號碼（例如：1,2,3）" required>
                        <button type="submit">產生預測</button>
                    </form>
                    <p>輸入的號碼: {{ numbers }}</p>
                    <p>預測號碼: {{ prediction }}</p>
                  </body>
                </html>
            """, numbers=numbers, prediction=prediction)
    return render_template_string("""
        <!DOCTYPE html>
        <html>
          <head>
            <title>6 號碼預測器</title>
          </head>
          <body style="text-align: center; padding-top: 100px;">
            <h1>6 號碼預測器</h1>
            <form method="POST">
                <input type="text" name="numbers" placeholder="輸入三個號碼（例如：1,2,3）" required>
                <button type="submit">產生預測</button>
            </form>
          </body>
        </html>
    """)

def generate_prediction():
    if len(history) < 3:
        return "請提供至少三期號碼"

    # 假設這裡會根據歷史號碼生成預測結果
    prediction = sorted([1, 2, 3, 4, 5, 6])  # 這個是靜態的預測示範，稍後可以加上具體邏輯
    return prediction

if __name__ == "__main__":
    app.run()
