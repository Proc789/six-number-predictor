from flask import Flask, render_template_string, request, redirect
import random

app = Flask(__name__)
history = []
predictions = []
hits = 0
total = 0
stage = 1
training = False

TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>6 號碼預測器 v3 強化版</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
  </head>
  <body style="max-width: 400px; margin: auto; padding-top: 50px; text-align: center; font-family: sans-serif;">
    <h2>6 號碼預測器 v3 強化版</h2>
    <form method="POST">
      <div>
        <input type="number" name="first" placeholder="冠軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <input type="number" name="second" placeholder="亞軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <input type="number" name="third" placeholder="季軍號碼" required style="width: 80%; padding: 8px;"><br><br>
        <button type="submit" style="padding: 10px 20px;">提交</button>
      </div>
    </form>
    <br>
    <a href="/toggle"><button>{{ toggle_text }}</button></a>
    {% if training %}
      <div><strong>訓練中...</strong></div>
      <div>命中率：{{ stats }}</div>
      <div>目前階段：第 {{ stage }} 關</div>
    {% endif %}
    {% if last_champion %}
      <br><div><strong>上期冠軍號碼：</strong>{{ last_champion }}</div>
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

@app.route("/", methods=["GET", "POST"])
def home():
    global hits, total, stage, training
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
                if last_champion in last_prediction:
                    hit = "命中"
                    if training:
                        hits += 1
                        stage = 1
                else:
                    hit = "未命中"
                    if training:
                        stage += 1
                if training:
                    total += 1

            if len(history) >= 3:
                prediction = generate_prediction()
                predictions.append(prediction)
                result = prediction
            else:
                result = "請至少輸入三期資料後才可預測"

        except:
            result = "格式錯誤，請輸入 1~10 的整數"

    toggle_text = "關閉訓練模式" if training else "啟動訓練模式"
    return render_template_string(TEMPLATE, result=result, history=history[-5:],
                                  last_champion=last_champion, last_prediction=last_prediction,
                                  hit=hit, training=training, toggle_text=toggle_text,
                                  stats=f"{hits} / {total}" if training else None,
                                  stage=stage if training else None)

@app.route("/toggle")
def toggle():
    global training, hits, total, stage
    training = not training
    if training:
        hits = 0
        total = 0
        stage = 1
    return redirect("/")

def generate_prediction():
    recent = history[-5:]
    flat = [n for group in recent for n in group]
    freq = {n: flat.count(n) for n in set(flat)}

    hot_candidates = sorted(freq.items(), key=lambda x: (-x[1], -last_index(x[0])))
    hot = hot_candidates[0][0]

    last_champion = history[-1][0]
    dynamic_hot = last_champion if last_champion != hot else next((n for n, _ in hot_candidates if n != hot), random.choice([n for n in range(1, 11) if n != hot]))

    cold_pool = [n for n in range(1, 6) if n not in (hot, dynamic_hot)]
    cold_freq = {n: flat.count(n) for n in cold_pool}
    min_freq = min(cold_freq.values()) if cold_freq else 0
    cold_candidates = [n for n in cold_pool if cold_freq[n] == min_freq]
    cold = random.choice(cold_candidates) if cold_candidates else random.choice(cold_pool)

    avoid = {hot, dynamic_hot, cold}
    all_numbers = set(range(1, 11))
    pool = list(all_numbers - avoid)

    prev_random = [n for n in predictions[-1] if n not in (hot, dynamic_hot, cold)] if predictions else []
    for _ in range(10):
        rands = random.sample(pool, 3)
        if len(set(rands) & set(prev_random)) <= 2:
            return sorted([hot, dynamic_hot, cold] + rands)
    return sorted([hot, dynamic_hot, cold] + random.sample(pool, 3))

def last_index(num):
    for i in range(len(history)-1, -1, -1):
        if num in history[i]:
            return i
    return -1

if __name__ == "__main__":
    app.run(debug=True)
