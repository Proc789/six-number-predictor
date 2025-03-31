from flask import Flask, render_template_string, request
import random

app = Flask(__name__)
history = []
predictions = []

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    last_champion = None
    last_prediction = None
    hit = None

    if request.method == "POST":
        try:
            first = int(request.form.get("first"))
            second = int(request.form.get("second"))
            third = int(request.form.get("third"))
            current = [first, second, third]
            history.append(current)

            if len(predictions) >= 1:
                last_prediction = predictions[-1]
                last_champion = current[0]
                hit = "命中" if last_champion in last_prediction else "未命中"

            if len(history) >= 3:
                prediction = generate_prediction()
                predictions.append(prediction)
                result = prediction
            else:
                result = "請至少輸入三期資料後才可預測"

        except:
            result = "格式錯誤，請輸入 1~10 的整數"

    return render_template_string(TEMPLATE, result=result, history=history[-5:],
                                  last_champion=last_champion, last_prediction=last_prediction, hit=hit)

def generate_prediction():
    recent = history[-3:]
    flat = [n for group in recent for n in group]
    freq = {n: flat.count(n) for n in set(flat)}
    max_freq = max(freq.values())
    hot_candidates = [n for n in freq if freq[n] == max_freq]
    for group in reversed(recent):
        for n in group:
            if n in hot_candidates:
                hot = n
                break
        else:
            continue
        break

    last_champion = history[-1][0]
    dynamic_hot = last_champion if last_champion != hot else next((n for n in hot_candidates if n != hot), random.choice([n for n in range(1, 11) if n != hot]))

    pool = [n for n in range(1, 11) if n not in (hot, dynamic_hot)]
    random.shuffle(pool)

    prev_random = []
    if len(predictions) > 0:
        prev_random = [n for n in predictions[-1] if n not in (hot, dynamic_hot)]

    for _ in range(10):
        rands = random.sample(pool, 4)
        if len(set(rands) & set(prev_random)) <= 2:
            return sorted([hot, dynamic_hot] + rands)

    return sorted([hot, dynamic_hot] + random.sample(pool, 4))

TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>6 號碼預測器</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
  </head>
  <body style="max-width: 400px; margin: auto; padding-top: 50px; text-align: center; font-family: sans-serif;">
    <h2>6 號碼預測器</h2>
    <form method="POST">
      <div>
        <input type="number" name="first" placeholder="冠軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <input type="number" name="second" placeholder="亞軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <input type="number" name="third" placeholder="季軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <button type="submit" style="padding: 10px 20px;">提交</button>
      </div>
    </form>
    <br>
    {% if last_champion %}
      <div><strong>上期冠軍號碼：</strong>{{ last_champion }}</div>
      <div><strong>是否命中：</strong>{{ hit }}</div>
      <div><strong>上期預測號碼：</strong>{{ last_prediction }}</div>
    {% endif %}
    {% if result %}
      <br><div><strong>下期預測號碼：</strong> {{ result }}</div>
    {% endif %}
    <br>
    <div style="text-align: left;">
      <strong>最近輸入紀錄：</strong>
      <ul>
        {% for row in history %}
          <li>{{ row }}</li>
        {% endfor %}
      </ul>
    </div>
  </body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
