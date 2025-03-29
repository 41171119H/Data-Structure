import os
import time
import pandas as pd
import sys
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError, ClientError

# 載入 .env 中的 GEMINI_API_KEY
load_dotenv()

# 分析項目
ITEMS = [
    "遺失地點是否具體",
    "是否包含毛色特徵",
    "是否有清楚的特徵描述",
    "遺失時間是否明確",
    "資料是否適合公告",
    "建議補充哪些資訊以增加協尋成功率",
    "是否有附圖片"
]

def parse_response_csv_line(response_line):
    parts = [part.strip() for part in response_line.split(',')]
    if len(parts) < 3:
        return {item: "" for item in ITEMS}
    result = {item: "" for item in ITEMS}
    for i, item in enumerate(ITEMS):
        if i < len(parts):
            result[item] = parts[i]
    return result

def build_analysis_input(row: pd.Series) -> str:
    fields = ["遺失地點", "毛色", "外觀", "特徵", "遺失時間", "PICTURE"]
    return "\n".join([f"{f}：{str(row[f])}" for f in fields if f in row])

def process_pet_business_batch(client, df_batch: pd.DataFrame, delimiter="-----"):
    entries = [build_analysis_input(row) for _, row in df_batch.iterrows()]
    example = "是,是,是,是,是,請補充個性特徵與是否有項圈,是"
    prompt = (
        "你是一位寵物協尋分析專家，請針對每筆走失寵物資料進行分析，並根據下列項目以 CSV 格式回覆：\n"
        + ",".join(ITEMS) + "\n"
        + "請依據每筆資料的『遺失地點』『毛色』『外觀』『特徵』『遺失時間』『PICTURE』等內容做出判斷。\n"
        + "請只回覆純粹的 CSV 格式，不需要額外解釋。每筆資料用以下分隔線分隔：\n"
        + f"{delimiter}\n"
        + "例如：\n"
        + ",".join(ITEMS) + "\n"
        + example + "\n"
        + f"{delimiter}\n" + example
    )
    batch_text = f"\n{delimiter}\n".join(entries)
    content = prompt + "\n\n" + batch_text

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=content
        )
    except (ServerError, ClientError) as e:
        print(f"API 呼叫失敗：{e}")
        return [{item: "" for item in ITEMS} for _ in entries]

    print("API 回傳內容：")
    parts = response.text.split(delimiter)
    results = []
    for idx, part in enumerate(parts):
        part = part.strip()
        print(f"[{idx}] → {part}")
        if part:
            results.append(parse_response_csv_line(part))
    if len(results) > len(entries):
        results = results[:len(entries)]
    elif len(results) < len(entries):
        results.extend([{item: "" for item in ITEMS}] * (len(entries) - len(results)))
    return results

def split_csv_file(input_file: str, lines_per_file: int = 1000):
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    total = len(df)
    for i in range(0, total, lines_per_file):
        part = df.iloc[i:i+lines_per_file]
        part.to_csv(f"loss{i//lines_per_file + 1}.csv", index=False, encoding="utf-8-sig")
    print("已完成分割資料。")

def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("請設定環境變數 GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_api_key)

    for i in range(1, 11):
        input_csv = f"loss{i}.csv"
        output_csv = f"pet_batch_output{i}.csv"
        if not os.path.exists(input_csv):
            print(f"找不到檔案：{input_csv}，跳過。")
            continue

        df = pd.read_csv(input_csv, encoding="utf-8-sig")
        batch_size = 100
        total = len(df)
        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            batch = df.iloc[start_idx:end_idx]
            try:
                batch_results = process_pet_business_batch(client, batch)
            except ClientError as e:
                print(f"遇到配額限制，暫停後重試：{e}")
                time.sleep(60)
                batch_results = process_pet_business_batch(client, batch)

            output_only_df = pd.DataFrame(batch_results)
            output_only_df.insert(0, "晶片號碼", batch["晶片號碼"].values)
            batch_df = output_only_df

            if start_idx == 0:
                batch_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
            else:
                batch_df.to_csv(output_csv, mode='a', index=False, header=False, encoding="utf-8-sig")
            print(f"{input_csv}：已處理 {end_idx} 筆 / {total}")
            time.sleep(1)

    print("全部處理完成。")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "split":
            split_csv_file("petLoss.csv")
        elif sys.argv[1] in ["-h", "--help", "help"]:
            print("""
使用方式:
  python pet_analyzer.py split           # 將 petLoss.csv 切成 loss*.csv
  python pet_analyzer.py                 # 依序處理 loss1.csv ~ loss10.csv
  python pet_analyzer.py loss1.csv       # 僅分析指定檔案 loss1.csv
  python pet_analyzer.py help            # 顯示這份說明
""")
        else:
            input_csv = sys.argv[1]
            gemini_api_key = os.environ.get("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("請設定環境變數 GEMINI_API_KEY")
            client = genai.Client(api_key=gemini_api_key)
            output_csv = f"pet_batch_output_{input_csv.replace('.csv', '')}.csv"
            df = pd.read_csv(input_csv, encoding="utf-8-sig")
            batch_size = 100
            total = len(df)
            for start_idx in range(0, total, batch_size):
                end_idx = min(start_idx + batch_size, total)
                batch = df.iloc[start_idx:end_idx]
                try:
                    batch_results = process_pet_business_batch(client, batch)
                except ClientError as e:
                    print(f"遇到配額限制，暫停後重試：{e}")
                    time.sleep(60)
                    batch_results = process_pet_business_batch(client, batch)

                output_only_df = pd.DataFrame(batch_results)
                output_only_df.insert(0, "晶片號碼", batch["晶片號碼"].values)
                batch_df = output_only_df

                if start_idx == 0:
                    batch_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
                else:
                    batch_df.to_csv(output_csv, mode='a', index=False, header=False, encoding="utf-8-sig")
                print(f"{input_csv}：已處理 {end_idx} 筆 / {total}")
                time.sleep(1)
            print(f"{input_csv} 分析完成，輸出為 {output_csv}")
