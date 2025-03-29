from flask import Flask, render_template, request
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 載入 API 金鑰
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    for col in ITEMS:
        if str(row[col]).strip() == "是":
            score += 1
    return score

@app.route("/", methods=["GET", "POST"])
def index():
    selected = {}
    results = []
    recommended_chip_ids = []
    search_keyword = ""
    filename = request.args.get("file", default="pet_batch_output1.csv")
    loss_file = filename.replace("pet_batch_output", "loss")

    if os.path.exists(filename) and os.path.exists(loss_file):
        df_analysis = pd.read_csv(filename)
        df_loss = pd.read_csv(loss_file)
        df_loss["晶片號碼"] = df_loss["晶片號碼"].astype(str).str.strip()
        df_analysis["晶片號碼"] = df_analysis["晶片號碼"].astype(str).str.strip()

        if request.method == "POST":
            feature_input = request.form.get("feature_input", "").strip()
            search_keyword = request.form.get("search_input", "").strip()

            if feature_input:
                # Step 1: 先進行關鍵字直接比對（品種、毛色、外觀、特徵）
                keywords = feature_input.strip().split()
                match_mask = df_loss.apply(
                    lambda row: any(
                        kw in str(row.get(field, "")) 
                        for kw in keywords 
                        for field in ["品種", "毛色", "外觀", "特徵"]
                    ),
                    axis=1
                )
                matched_loss = df_loss[match_mask]

                if not matched_loss.empty:
                    matched_chip_ids = matched_loss["晶片號碼"].tolist()
                    print(f"✅ 直接關鍵字命中 {len(matched_chip_ids)} 筆")
                    filtered_loss = matched_loss
                    filtered_analysis = df_analysis[df_analysis["晶片號碼"].isin(matched_chip_ids)]
                    df = pd.merge(filtered_analysis, filtered_loss, on="晶片號碼", how="left")
                    df["完整度分數"] = df.apply(calculate_score, axis=1)
                    recommended_chip_ids = matched_chip_ids  # 讓前端知道有推薦數
                else:
                    # Step 2: 若完全無命中，再使用 Gemini AI 推測
                    prompt = (
                        f"請根據以下走失特徵描述：「{feature_input}」，"
                        "從資料中找出最可能符合的紀錄（根據品種、毛色、外觀、特徵），"
                        "僅回覆晶片號碼，每行一個，最多 20 筆，不要加入任何文字說明。\n\n"
                        "例如：\n990000000123456\n900073000429121"
                    )

                    records = []
                    for _, row in df_loss.iterrows():
                        desc = f"晶片號碼：{row['晶片號碼']}，品種：{row.get('品種','')}，毛色：{row.get('毛色','')}，外觀：{row.get('外觀','')}，特徵：{row.get('特徵','')}"
                        records.append(desc)

                    full_prompt = prompt + "\n\n" + "\n".join(records[:1000])

                    try:
                        model = genai.GenerativeModel("gemini-1.5-pro-latest")
                        response = model.generate_content(full_prompt)
                        response_text = response.text

                        recommended_chip_ids = [
                            line.strip() for line in response_text.strip().splitlines()
                            if line.strip().isdigit()
                        ]

                        if recommended_chip_ids:
                            filtered_loss = df_loss[df_loss["晶片號碼"].isin(recommended_chip_ids)]
                            filtered_analysis = df_analysis[df_analysis["晶片號碼"].isin(recommended_chip_ids)]
                            df = pd.merge(filtered_analysis, filtered_loss, on="晶片號碼", how="left")
                            df["完整度分數"] = df.apply(calculate_score, axis=1)
                            print(f"🤖 Gemini 推薦 {len(recommended_chip_ids)} 筆，成功比對 {len(df)} 筆資料")
                        else:
                            print("⚠️ Gemini 沒有回傳有效晶片號碼。")
                            df = pd.DataFrame()
                        print("✅ Gemini 回傳內容：\n", response_text)
                    except Exception as e:
                        print("Gemini 分析失敗：", e)
                        df = pd.DataFrame()

            else:
                df = pd.merge(df_analysis, df_loss, on="晶片號碼", how="left")
                df["完整度分數"] = df.apply(calculate_score, axis=1)

            if search_keyword:
                df = df[
                    df["晶片號碼"].astype(str).str.contains(search_keyword, na=False) |
                    df.get("寵物名", "").astype(str).str.contains(search_keyword, na=False)
                ]

            for item in ITEMS:
                val = request.form.get(item)
                if val:
                    selected[item] = val
            for k, v in selected.items():
                if k in df.columns:
                    df = df[df[k] == v]

            df = df.sort_values(by="完整度分數", ascending=False)
            results = df.to_dict(orient="records")

    return render_template(
        "index.html",
        items=ITEMS,
        results=results,
        selected=selected,
        recommended_count=len(recommended_chip_ids),
        search_input=search_keyword
    )

if __name__ == "__main__":
    app.run(debug=True)
