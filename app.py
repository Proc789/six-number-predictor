from flask import Flask, render_template_string, request
import random

app = Flask(__name__)
history = []  # 累積輸入的前三名開獎號碼

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
        try:
            numbers = list(map(int, request.form.get("numbers").split(",")))
            if len(numbers) == 3:
                history.append(numbers)
                if len(history) >= 3:
                    prediction = generate_prediction()
                else:
                    prediction = "請輸入至少三期資料"
            else:
                prediction = "請輸入三個號碼"
        except:
            prediction = "格式錯誤，請用逗號分隔三個數字"

    return render_template_string(TEMPLATE, prediction=prediction, history=history[-5:])

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
    if len(history) > 1:
        prev_full = generate_prediction_once(history[-2])
        prev_random = [n for n in prev_full if n not in (hot, dynamic_hot)]

    for _ in range(10):
        rands = random.sample(pool, 4)
        if len(set(rands) & set(prev_random)) <= 2:
            return sorted([hot, dynamic_hot] + rands)

    return sorted([hot, dynamic_hot] + random.sample(pool, 4))

def generate_prediction_once(fake_history):
    recent = history[-3:] if len(history) >= 3 else [fake_history]
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
    last_champion = fake_history[0]
    dynamic_hot = last_champion if last_champion != hot else next((n for n in hot_candidates if n != hot), random.choice([n for n in range(1, 11) if n != hot]))
    pool = [n for n in range(1, 11) if n not in (hot, dynamic_hot)]
    return sorted([hot, dynamic_hot] + random.sample(pool, 4))

TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>6 號碼預測器</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body style="max-width: 400px; margin: auto; padding-top: 50px; text-align: center; font-family: sans-serif;">
    <h2>6 號碼預測器</h2>
    <form method="POST">
      <input type="text" name="numbers" placeholder="例如：4,6,8" style="width: 80%; padding: 8px;">
      <br><br>
      <button type="submit" style="padding: 10px 20px;">提交</button>
    </form>
    <br>
    {% if prediction %}
      <div><strong>預測號碼：</strong> {{ prediction }}</div>
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
