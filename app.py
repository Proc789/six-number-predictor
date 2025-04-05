from flask import Flask, render_template_string, request, redirect
import random
from collections import Counter

app = Flask(__name__)
history = []
predictions = []
source_logs = []
debug_logs = []
training_enabled = False
current_stage = 1
hot_hits = 0
dynamic_hits = 0
extra_hits = 0
all_hits = 0
total_tests = 0

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>6碼預測器</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>6碼預測器</h2>
  <div style='font-size: 14px;'>版本：熱2 + 動熱2 + 補碼2（公版UI）</div>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')" inputmode="numeric"><br><br>
    <input name='second' id='second' placeholder='亞軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')" inputmode="numeric"><br><br>
    <input name='third' id='third' placeholder='季軍' required style='width: 80%; padding: 8px;' inputmode="numeric"><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>
  <br>
  <a href='/toggle'><button>{{ '關閉統計模式' if training else '啟動統計模式' }}</button></a>
  <a href='/reset'><button style='margin-left: 10px;'>清除所有資料</button></a>

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
      冠軍命中次數（任一區）：{{ all_hits }} / {{ total_tests }}<br>
      熱號命中次數：{{ hot_hits }} / {{ total_tests }}<br>
      動熱命中次數：{{ dynamic_hits }} / {{ total_tests }}<br>
      補碼命中次數：{{ extra_hits }} / {{ total_tests }}<br>
    </div>
  {% endif %}

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
    global training_enabled, predictions, history
    global current_stage, hot_hits, dynamic_hits, extra_hits, all_hits, total_tests

    prediction = None
    last_prediction = predictions[-1] if predictions else None

    if request.method == 'POST':
        try:
            first = int(request.form['first']) or 10
            second = int(request.form['second']) or 10
            third = int(request.form['third']) or 10
            current = [first, second, third]
            history.append(current)

            if len(history) >= 5:
                result = make_prediction()
                predictions.append(result)
                prediction = result

                if len(predictions) >= 2:
                    champion = current[0]
                    last = predictions[-2]

                    if training_enabled:
                        total_tests += 1
                        if champion in last:
                            all_hits += 1
                            current_stage = 1
                        else:
                            current_stage += 1

                        if champion in result[:2]:
                            hot_hits += 1
                            label = "熱號命中"
                        elif champion in result[2:4]:
                            dynamic_hits += 1
                            label = "動熱命中"
                        elif champion in result[4:]:
                            extra_hits += 1
                            label = "補碼命中"
                        else:
                            label = "未命中"

                        source_logs.append(f"冠軍號碼 {champion} → {label}")
                        debug_logs.append(f"熱號 = {result[:2]} ｜動熱 = {result[2:4]} ｜補碼 = {result[4:]} ｜冠軍 = {champion}（{label}）")
        except:
            prediction = ["格式錯誤"]

    return render_template_string(TEMPLATE,
        prediction=prediction,
        last_prediction=last_prediction,
        stage=current_stage,
        history_data=history[-10:],
        result_log=source_logs[-10:],
        debug_log=debug_logs[-10:],
        training=training_enabled,
        hot_hits=hot_hits,
        dynamic_hits=dynamic_hits,
        extra_hits=extra_hits,
        all_hits=all_hits,
        total_tests=total_tests
    )

@app.route('/toggle')
def toggle():
    global training_enabled, hits, total, stage, current_stage
    global hot_hits, dynamic_hits, extra_hits, all_hits, total_tests
    training_enabled = not training_enabled
    hits = total = current_stage = 1
    hot_hits = dynamic_hits = extra_hits = all_hits = total_tests = 0
    return redirect('/')

@app.route('/reset')
def reset():
    global history, predictions, current_stage
    global hot_hits, dynamic_hits, extra_hits, all_hits, total_tests
    global source_logs, debug_logs
    history = []
    predictions = []
    current_stage = 1
    hot_hits = dynamic_hits = extra_hits = all_hits = total_tests = 0
    source_logs = []
    debug_logs = []
    return redirect('/')

def make_prediction():
    recent = history[-3:]
    flat = [n for group in recent for n in group]
    freq = Counter(flat)
    top_hot = sorted(freq.items(), key=lambda x: (-x[1], -flat[::-1].index(x[0])))[:3]
    hot = random.sample([n for n, _ in top_hot], k=min(2, len(top_hot)))

    flat_dyn = [n for n in flat if n not in hot]
    freq_dyn = Counter(flat_dyn)
    dyn_top = sorted(freq_dyn.items(), key=lambda x: (-x[1], -flat_dyn[::-1].index(x[0])))[:3]
    dynamic_hot = random.sample([n for n, _ in dyn_top], k=min(2, len(dyn_top)))

    used = set(hot + dynamic_hot)
    pool = [n for n in range(1, 11) if n not in used]
    random.shuffle(pool)
    extra = pool[:2]

    return sorted(hot + dynamic_hot + extra)

if __name__ == '__main__':
    app.run(debug=True)
