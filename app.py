from flask import Flask, render_template_string, request
import random
from collections import Counter

app = Flask(__name__)
history = []
predictions = []
source_logs = []
debug_logs = []

hot_hits = 0
dynamic_hits = 0
extra_hits = 0
all_hits = 0
total_tests = 0
current_stage = 1

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>6碼預測器（hotplus v2-6碼版）</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>6碼預測器（hotplus v2-6碼版）</h2>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')"><br><br>
    <input name='second' id='second' placeholder='亞軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')"><br><br>
    <input name='third' id='third' placeholder='季軍' required style='width: 80%; padding: 8px;'><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>

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

  <div style='margin-top: 20px; text-align: left;'>
    <strong>命中統計：</strong><br>
    冠軍命中次數（任一區）：{{ all_hits }} / {{ total_tests }}<br>
    熱號命中次數：{{ hot_hits }} / {{ total_tests }}<br>
    動熱命中次數：{{ dynamic_hits }} / {{ total_tests }}<br>
    補碼命中次數：{{ extra_hits }} / {{ total_tests }}<br>
  </div>

  {% if history_data %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>最近輸入紀錄：</strong>
      <ul>
        {% for row in history_data %}
          <li>第 {{ loop.index }} 期：{{ row }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  {% if result_log %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>來源紀錄（冠軍號碼分類）：</strong>
      <ul>
        {% for row in result_log %}
          <li>第 {{ loop.index }} 期：{{ row }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  {% if debug_log %}
    <div style='margin-top: 20px; text-align: left; font-size: 13px; color: #555;'>
      <strong>除錯紀錄（每期來源分析）：</strong>
      <ul>
        {% for row in debug_log %}
          <li>第 {{ loop.index }} 期：{{ row }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

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

@app.route('/', methods=['GET', 'POST'])
def index():
    global hot_hits, dynamic_hits, extra_hits, all_hits, total_tests, current_stage
    prediction = None
    last_prediction = predictions[-1] if predictions else None

    if request.method == 'POST':
        try:
            first = int(request.form['first']) or 10
            second = int(request.form['second']) or 10
            third = int(request.form['third']) or 10
            current = [first, second, third]
            history.append(current)

            if len(history) >= 3:
                recent = history[-3:]
                flat = [n for group in recent for n in group]
                freq = Counter(flat)
                top_hot = sorted(freq.items(), key=lambda x: (-x[1], -flat[::-1].index(x[0])))[:3]
                hot_pool = [n for n, _ in top_hot]
                hot = random.sample(hot_pool, k=min(2, len(hot_pool)))

                flat_dynamic = [n for group in recent for n in group if n not in hot]
                freq_dyn = Counter(flat_dynamic)
                dynamic_pool = sorted(freq_dyn, key=lambda x: (-freq_dyn[x], -flat_dynamic[::-1].index(x)))[:3]
                dynamic_hot = random.sample(dynamic_pool, k=min(2, len(dynamic_pool)))

                used = set(hot + dynamic_hot)
                pool = [n for n in range(1, 11) if n not in used]
                random.shuffle(pool)
                extra = pool[:2]  # 選兩碼補碼 → 6 碼總數

                result = sorted(hot + dynamic_hot + extra)
                prediction = result
                predictions.append(result)

                champion = current[0]
                total_tests += 1

                if last_prediction and champion in last_prediction:
                    all_hits += 1
                    current_stage = 1
                else:
                    current_stage += 1

                if champion in hot:
                    hot_hits += 1
                    label = "熱號命中"
                elif champion in dynamic_hot:
                    dynamic_hits += 1
                    label = "動熱命中"
                elif champion in extra:
                    extra_hits += 1
                    label = "補碼命中"
                else:
                    label = "未命中"

                source_logs.append(f"冠軍號碼 {champion} → {label}")
                debug_logs.append(
                    f"熱號 = {hot} ｜動熱 = {dynamic_hot} ｜補碼 = {extra} ｜冠軍 = {champion}（{label}）"
                )

        except:
            prediction = ["格式錯誤"]

    return render_template_string(TEMPLATE,
        prediction=prediction,
        last_prediction=last_prediction,
        stage=current_stage,
        history_data=history[-10:],
        result_log=source_logs[-10:],
        debug_log=debug_logs[-10:],
        hot_hits=hot_hits,
        dynamic_hits=dynamic_hits,
        extra_hits=extra_hits,
        all_hits=all_hits,
        total_tests=total_tests)

if __name__ == '__main__':
    app.run(debug=True)
