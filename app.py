from flask import Flask, render_template_string, redirect
import random
import requests

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
  <title>5 號碼預測器</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style="max-width: 400px; margin: auto; padding-top: 50px; text-align: center; font-family: sans-serif;">
  <h2>5 號碼預測器</h2>
  <form method="POST">
    <button type="submit">抓取開獎 + 預測</button>
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

def get_latest_top3():
    try:
        url = "https://ar1.ar198.com/api_r/get/result"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://ar1.ar198.com/",
        }
        res = requests.post(url, headers=headers)
        data = res.json()
        return data["data"]["list"][0]["last"]["n"][:3]
    except Exception as e:
        print("❌ 無法取得開獎號碼：", e)
        return []

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

    # 找冷號（出現最少次）
    cold_freq = {n: flat.count(n) for n in range(1, 11)}
    min_count = min(cold_freq.values())
    cold_candidates = [n for n in range(1, 6) if cold_freq.get(n, 0) == min_count and n not in (hot, dynamic_hot)]
    cold = random.choice(cold_candidates) if cold_candidates else random.choice([n for n in range(1, 6) if n not in (hot, dynamic_hot)])

    avoid = {hot, dynamic_hot, cold}
    pool = [n for n in range(1, 11) if n not in avoid]
    random.shuffle(pool)
    rands = random.sample(pool, 2)

    return sorted([hot, dynamic_hot, cold] + rands)

@app.route("/", methods=["GET", "POST"])
def index():
    global hits, total, stage, training
    result = None
    last_champion = None
    last_prediction = None
    hit = None

    if len(history) >= 3:
        prediction = generate_prediction()
        predictions.append(prediction)
        result = prediction

    if len(predictions) >= 1:
        current = get_latest_top3()
        if current:
            history.append(current)
            last_prediction = predictions[-1]
            last_champion = current[0]
            hit = "命中" if last_champion in last_prediction else "未命中"
            if training:
                total += 1
                if hit == "命中":
                    hits += 1
                    stage = 1
                else:
                    stage += 1

    toggle_text = "關閉訓練模式" if training else "啟動訓練模式"
    return render_template_string(TEMPLATE, result=result, history=history[-10:],
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

if __name__ == "__main__":
    app.run(debug=True)
