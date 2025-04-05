from flask import Flask, render_template_string, request, redirect
import random
from collections import Counter

app = Flask(__name__)
history = []
predictions = []
stage = 1
training = False
hits = 0
total = 0

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>6碼預測器</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>6碼預測器</h2>
  <div style='margin-bottom: 10px;'>版本：熱號2 + 動熱2 + 補碼2</div>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍號碼' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')" inputmode="numeric"><br><br>
    <input name='second' id='second' placeholder='亞軍號碼' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')" inputmode="numeric"><br><br>
    <input name='third' id='third' placeholder='季軍號碼' required style='width: 80%; padding: 8px;' inputmode="numeric"><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>

  <br>
  <a href='/toggle'><button>{{ '關閉訓練模式' if training else '啟動訓練模式' }}</button></a>
  <a href='/reset'><button style='margin-left:10px;'>清除所有紀錄</button></a>

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
      冠軍命中次數（任一區）：{{ hits }} / {{ total }}
    </div>
  {% endif %}

  {% if history %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>最近輸入紀錄：</strong>
      <ul>
        {% for row in history %}
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
    global stage, predictions, hits, total

    prediction = None
    last_prediction = predictions[-1] if predictions else None

    if request.method == 'POST':
        try:
            first = int(request.form['first'])
            second = int(request.form['second'])
            third = int(request.form['third'])

            first = 10 if first == 0 else first
            second = 10 if second == 0 else second
            third = 10 if third == 0 else third

            current = [first, second, third]
            history.append(current)

            if len(history) >= 6:
                last_champion = history[-1][0]
                prev_prediction = predictions[-1]
                if last_champion in prev_prediction:
                    if training:
                        hits += 1
                        stage = 1
                else:
                    if training:
                        stage += 1
                if training:
                    total += 1

            if len(history) >= 5:
                prediction = generate_prediction()
                predictions.append(prediction)

        except:
            prediction = ['格式錯誤']

    return render_template_string(TEMPLATE,
        prediction=prediction,
        last_prediction=last_prediction,
        history=history[-10:],
        stage=stage,
        training=training,
        hits=hits,
        total=total)

@app.route('/toggle')
def toggle():
    global training, hits, total, stage
    training = not training
    hits = 0
    total = 0
    stage = 1
    return redirect('/')

@app.route('/reset')
def reset():
    global history, predictions, hits, total, stage
    history = []
    predictions = []
    hits = 0
    total = 0
    stage = 1
    return redirect('/')

def generate_prediction():
    recent = history[-3:]
    flat = [n for g in recent for n in g]
    freq = Counter(flat)

    hot = [n for n, _ in freq.most_common(3)][:2]
    dynamic_pool = [n for n in freq if n not in hot]
    dynamic_sorted = sorted(dynamic_pool, key=lambda x: (-freq[x], -flat[::-1].index(x)))
    dynamic = dynamic_sorted[:2]

    exclude = set(hot + dynamic + dynamic_sorted)
    pool = [n for n in range(1, 11) if n not in exclude]
    random.shuffle(pool)
    extra = pool[:2]

    result = hot + dynamic + extra
    return sorted(result)

if __name__ == '__main__':
    app.run(debug=True)
