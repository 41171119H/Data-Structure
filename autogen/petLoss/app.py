from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

ITEMS = [
    "遺失地點是否具體",
    "是否包含毛色特徵",
    "是否有清楚的特徵描述",
    "遺失時間是否明確",
    "資料是否適合公告",
    "是否有附圖片"
]

def calculate_score(row):
    score = 0
    for col in [
        "遺失地點是否具體",
        "是否包含毛色特徵",
        "是否有清楚的特徵描述",
        "遺失時間是否明確",
        "是否有附圖片"
    ]:
        if str(row[col]).strip() == "是":
            score += 1
    return score

@app.route("/", methods=["GET", "POST"])
def index():
    selected = {}
    results = pd.DataFrame()
    filename = request.args.get("file", default="pet_batch_output1.csv")
    loss_file = filename.replace("pet_batch_output", "loss")

    if os.path.exists(filename) and os.path.exists(loss_file):
        df_analysis = pd.read_csv(filename)
        df_loss = pd.read_csv(loss_file)
        df = pd.merge(df_analysis, df_loss, on="晶片號碼", how="left")
        df["完整度分數"] = df.apply(calculate_score, axis=1)

        if request.method == "POST":
            for item in ITEMS:
                val = request.form.get(item)
                if val:
                    selected[item] = val
            for k, v in selected.items():
                df = df[df[k] == v]
            df = df.sort_values(by="完整度分數", ascending=False)

        results = df

    return render_template("index.html", items=ITEMS, results=results, selected=selected)

if __name__ == "__main__":
    app.run(debug=True)
