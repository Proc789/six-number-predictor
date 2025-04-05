from flask import Flask, render_template_string, request, redirect
import random
from collections import Counter

app = Flask(__name__)
history = []
predictions = []
sources = []
debug_logs = []
hits = 0
hot_hits = 0
dynamic_hits = 0
extra_hits = 0
total = 0
stage = 1
training = False

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>6碼預測器</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>6碼預測器</h2>
  <div>版本：熱2 + 動2 + 補2</div>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')" inputmode="numeric"><br><br>
    <input name='second' id='second' placeholder='亞軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')" inputmode="numeric"><br><br>
    <input name='third' id='third' placeholder='季軍' required style='width: 80%; padding: 8px;' inputmode="numeric"><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>
  <br>
  <a href='/toggle'><button>{{ '關閉統計模式' if training else '啟動統計模式' }}</button></a>
  <a href='/reset'><button style='margin-left: 10px;'>清除所有紀錄</button></a>

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
      冠軍命中次數（任一區）：{{ hits }} / {{ total }}<br>
      熱號命中次數：{{ hot_hits }}<br>
      動熱命中次數：{{ dynamic_hits }}<br>
      補碼命中次數：{{ extra_hits }}<br>
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
    global predictions, hits, hot_hits, dynamic_hits, extra_hits, total, stage, training
    prediction = None
    last_prediction = predictions[-1] if predictions else None

    if request.method == 'POST':
        try:
            first = int(request.form['first']) or 10
            second = int(request.form['second']) or 10
            third = int(request.form['third']) or 10
            current = [first, second, third]
            history.append(current)

            if len(history) >= 5 or training:
                prediction = make_prediction()
                predictions.append(prediction)

                if len(predictions) >= 2:
                    champion = current[0]
                    total += 1
                    if champion in predictions[-2]:
                        hits += 1
                        stage = 1
                    else:
                        stage += 1

                    if champion in sources[-1]['hot']:
                        hot_hits += 1
                    elif champion in sources[-1]['dynamic']:
                        dynamic_hits += 1
                    elif champion in sources[-1]['extra']:
                        extra_hits += 1
        except:
            prediction = ['格式錯誤']

    return render_template_string(TEMPLATE,
        prediction=prediction,
        last_prediction=last_prediction,
        stage=stage,
        history_data=history[-10:],
        training=training,
        hits=hits,
        total=total,
        hot_hits=hot_hits,
        dynamic_hits=dynamic_hits,
        extra_hits=extra_hits)

@app.route('/toggle')
def toggle():
    global training, hits, total, stage, predictions
    training = not training
    hits = 0
    total = 0
    stage = 1
    predictions = []
    return redirect('/')

@app.route('/reset')
def reset():
    global history, predictions, hits, total, stage, training, sources, debug_logs, hot_hits, dynamic_hits, extra_hits
    history.clear()
    predictions.clear()
    sources.clear()
    debug_logs.clear()
    hits = total = stage = 1
    hot_hits = dynamic_hits = extra_hits = 0
    training = False
    return redirect('/')

def make_prediction():
    recent = history[-3:]
    flat = [n for r in recent for n in r]
    freq = Counter(flat)
    hot = [n for n, _ in freq.most_common(3)][:2]

    dynamic_pool = [n for n in freq if n not in hot]
    dynamic_sorted = sorted(dynamic_pool, key=lambda x: (-freq[x], -flat[::-1].index(x)))
    dynamic = dynamic_sorted[:2]

    exclude = set(hot + dynamic)
    pool = [n for n in range(1, 11) if n not in exclude]
    random.shuffle(pool)
    extra = pool[:2]

    sources.append({"hot": hot, "dynamic": dynamic, "extra": extra})
    return sorted(hot + dynamic + extra)

if __name__ == '__main__':
    app.run(debug=True)
