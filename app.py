from flask import Flask, render_template_string, request, redirect
import random
from collections import Counter

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
  <title>6碼預測器（公版UI）</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>6碼預測器</h2>
  <div style='font-size: 14px; color: #555;'>版本：熱號2 + 動熱2 + 補碼2</div>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')" inputmode="numeric"><br><br>
    <input name='second' id='second' placeholder='亞軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')" inputmode="numeric"><br><br>
    <input name='third' id='third' placeholder='季軍' required style='width: 80%; padding: 8px;' inputmode="numeric"><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>
  <br>
  <a href="/toggle"><button>{{ toggle_text }}</button></a>
  <a href="/clear"><button>清除所有紀錄</button></a>

  {% if prediction %}
    <div style='margin-top: 20px;'>
      <strong>本期預測號碼：</strong> {{ prediction }}（目前第 {{ stage }} 關）
    </div>
  {% endif %}
  {% if last_prediction %}
    <div style='margin-top: 10px;'>
      <strong>上期預測號碼：</strong> {{ last_prediction }}
    </div>
  {% endif %}
  {% if training %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>命中統計：</strong><br>
      命中次數：{{ hits }} / {{ total }}<br>
    </div>
  {% endif %}

  <div style='margin-top: 20px; text-align: left;'>
    <strong>最近輸入紀錄：</strong>
    <ul>
      {% for row in history_data %}
        <li>第 {{ loop.index }} 期：{{ row }}</li>
      {% endfor %}
    </ul>
  </div>

  <script>
    function moveToNext(current, nextId) {
      setTimeout(() => {
        if (current.value === '0') current.value = '10';
        let val = parseInt(current.value);
        if (!isNaN(val) && val >= 1 && val <= 10) {
          document.getElementById(nextId).focus();
        }
      }, 100);
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    global history, predictions, hits, total, stage, training
    prediction = None
    last_prediction = predictions[-1] if predictions else None

    if request.method == "POST":
        try:
            first = int(request.form["first"]) or 10
            second = int(request.form["second"]) or 10
            third = int(request.form["third"]) or 10
            current = [first, second, third]
            history.append(current)

            if len(predictions) >= 1:
                last_champion = current[0]
                if last_champion in last_prediction:
                    if training:
                        hits += 1
                        stage = 1
                else:
                    if training:
                        stage += 1
                if training:
                    total += 1

            if len(history) >= 3:
                prediction = generate_prediction()
                predictions.append(prediction)
        except:
            prediction = ["格式錯誤"]

    toggle_text = "關閉訓練模式" if training else "啟動訓練模式"
    return render_template_string(TEMPLATE,
        prediction=prediction,
        last_prediction=last_prediction,
        stage=stage,
        training=training,
        toggle_text=toggle_text,
        hits=hits,
        total=total,
        history_data=history[-10:]
    )

@app.route("/toggle")
def toggle():
    global training, hits, total, stage
    training = not training
    hits = 0
    total = 0
    stage = 1
    return redirect("/")

@app.route("/clear")
def clear():
    global history, predictions, hits, total, stage
    history.clear()
    predictions.clear()
    hits = 0
    total = 0
    stage = 1
    return redirect("/")

def generate_prediction():
    recent = history[-3:]
    flat = [n for g in recent for n in g]
    freq = Counter(flat)
    hot_pool = sorted(freq.items(), key=lambda x: (-x[1], -flat[::-1].index(x[0])))[:3]
    hot = random.sample([n for n, _ in hot_pool], k=min(2, len(hot_pool)))

    flat_dynamic = [n for n in flat if n not in hot]
    freq_dyn = Counter(flat_dynamic)
    dynamic_pool = sorted(freq_dyn, key=lambda x: (-freq_dyn[x], -flat_dynamic[::-1].index(x)))[:4]
    dynamic_hot = random.sample(dynamic_pool, k=min(2, len(dynamic_pool)))

    used = set(hot + dynamic_hot)
    pool = [n for n in range(1, 11) if n not in used]
    random.shuffle(pool)
    extra = pool[:2]

    result = sorted(hot + dynamic_hot + extra)
    return result

if __name__ == "__main__":
    app.run(debug=True)
