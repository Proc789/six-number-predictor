# 6碼分析器 - 追關版（5關邏輯，固定熱2+動2+補2）
from flask import Flask, render_template_string, request, redirect
import random
from collections import Counter

app = Flask(__name__)
history = []
predictions = []
sources = []
hot_hits = 0
dynamic_hits = 0
extra_hits = 0
all_hits = 0
total_tests = 0
current_stage = 1
training_enabled = False
rhythm_history = []
rhythm_state = "未知"
last_champion_zone = ""
was_observed = False
observation_message = ""

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>預測器</title>
</head>
<body style='max-width: 400px; margin: auto; padding-top: 40px; font-family: sans-serif; text-align: center;'>
  <h2>預測器</h2>
  <div>版本：6碼分析器・追關版（5關）</div>
  <form method='POST'>
    <input name='first' id='first' placeholder='冠軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'second')" inputmode="numeric"><br><br>
    <input name='second' id='second' placeholder='亞軍' required style='width: 80%; padding: 8px;' oninput="moveToNext(this, 'third')" inputmode="numeric"><br><br>
    <input name='third' id='third' placeholder='季軍' required style='width: 80%; padding: 8px;' inputmode="numeric"><br><br>
    <button type='submit' style='padding: 10px 20px;'>提交</button>
  </form>
  <br>
  <form method='GET' action='/observe' onsubmit="syncBeforeObserve()">
    <input type='hidden' name='first' id='first_obs'>
    <input type='hidden' name='second' id='second_obs'>
    <input type='hidden' name='third' id='third_obs'>
    <button type='submit'>觀察本期</button>
  </form>
  <a href='/toggle'><button>{{ '關閉統計模式' if training else '啟動統計模式' }}</button></a>
  <a href='/reset'><button style='margin-left: 10px;'>清除所有資料</button></a>
  {% if prediction %}
    <div style='margin-top: 20px;'>
      <strong>本期預測號碼：</strong> {{ prediction }}（目前第 {{ stage }} 關）<br>
      預測碼數量：{{ prediction|length }} 碼
    </div>
  {% endif %}
  {% if last_prediction %}
    <div style='margin-top: 10px;'>
      <strong>上期預測號碼：</strong> {{ last_prediction }}
    </div>
  {% endif %}
  {% if last_champion_zone %}<div>冠軍號碼開在：{{ last_champion_zone }}</div>{% endif %}
  {% if observation_message %}<div style='color: gray;'>{{ observation_message }}</div>{% endif %}
  <div>熱號節奏狀態：{{ rhythm_state }}</div>
  {% if training %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>命中統計：</strong><br>
      冠軍命中次數（任一區）：{{ all_hits }} / {{ total_tests }}<br>
      熱號命中次數：{{ hot_hits }}<br>
      動熱命中次數：{{ dynamic_hits }}<br>
      補碼命中次數：{{ extra_hits }}<br>
    </div>
  {% endif %}
  {% if history %}
    <div style='margin-top: 20px; text-align: left;'>
      <strong>最近輸入紀錄：</strong>
      <ul>
        {% for row in history[-10:] %}<li>{{ row }}</li>{% endfor %}
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
        document.getElementById('first_obs').value = document.getElementById('first').value;
        document.getElementById('second_obs').value = document.getElementById('second').value;
        document.getElementById('third_obs').value = document.getElementById('third').value;
      }, 100);
    }
    function syncBeforeObserve() {
      document.getElementById('first_obs').value = document.getElementById('first').value;
      document.getElementById('second_obs').value = document.getElementById('second').value;
      document.getElementById('third_obs').value = document.getElementById('third').value;
    }
  </script>
</body>
</html>
"""

# 預測邏輯更新為：熱號2 + 動熱2 + 補碼2（共6碼）
def make_prediction(stage):
    recent = history[-3:]
    flat = [n for g in recent for n in g]
    freq = Counter(flat)

    hot = [n for n, _ in freq.most_common(3)][:2]
    dynamic_pool = [n for n in freq if n not in hot]
    dynamic_sorted = sorted(dynamic_pool, key=lambda x: (-freq[x], -flat[::-1].index(x)))
    dynamic = dynamic_sorted[:2]

    h = hot[:2]
    d = dynamic[:2]
    used = set(h + d)
    pool = [n for n in range(1, 11) if n not in used]
    random.shuffle(pool)
    extra = pool[:2]  # 改為補2碼

    sources.append({'hot': h, 'dynamic': d, 'extra': extra})
    return sorted(h + d + extra)
