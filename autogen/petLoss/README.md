
# 🐾 Lost Pet Dataset AI Analysis & Search Platform

A Flask-based AI-powered web platform for analyzing and searching lost pet data.  
This project combines structured evaluation with Gemini API to enhance pet recovery efforts through intelligent recommendations and interactive filtering.

---

## 📁 Dataset Description

The main dataset is in `CSV` format (`petLoss.csv`) with the following fields:

- `晶片號碼` (Chip number)  
- `寵物名` (Pet name)  
- `寵物別`, `性別` (Pet type & gender)  
- `品種` (Breed)  
- `毛色` (Color)  
- `外觀`, `特徵` (Appearance, features)  
- `遺失時間`, `遺失地點` (Lost time & location)  
- `飼主姓名`, `連絡電話`, `Email`  
- `PICTURE` (Image link)

---

## 🤖 AI Analysis: `pet_analyzer.py`

### Analysis Targets (Gemini)

Each record is evaluated on the following criteria:

- 是否提供具體且詳細的遺失地點（是否具體）
- 毛色與外觀描述是否足夠辨識
- 是否有明顯的個別特徵（如斷尾、異色眼）
- 遺失時間是否明確（有日期與時間）
- 是否有清晰圖片
- 是否適合公告
- 建議補充哪些資訊（例如個性、是否結紮）

### Prompt Strategy

- The script constructs a batch prompt to Gemini API with 100 records per request.
- Responses are structured CSV strings separated by delimiters.
- Each result is parsed and written to new CSV output.

### Input / Output

- Input:
  - `petLoss.csv` or split files: `loss1.csv`, `loss2.csv`, ...
- Output:
  - `pet_batch_output1.csv`, `pet_batch_output2.csv`, ...

---

## 🌐 Web Interface: `app.py`

Built with Flask, the web interface provides:

- File loading via `?file=pet_batch_output1.csv`
- Merge with `loss1.csv` for full context
- Filtering based on AI-evaluated fields
- Additional manual search:
  - 🔍 Chip number or pet name keyword
  - 🧠 AI-assisted feature search via Gemini

### Web Features

- Sort by completeness score (based on AI fields)
- Search and filter simultaneously
- Easy data browsing and review

---

## 🧪 How to Use

### Step 1️⃣ – Split the Dataset  
Split the original file into chunks of 1000 records:  
```bash
python pet_analyzer.py split
```

### Step 2️⃣ – Analyze All Files  
Batch process all split files using Gemini:  
```bash
python pet_analyzer.py
```

### Step 3️⃣ – Analyze a Specific File  
Analyze a single CSV file:  
```bash
python pet_analyzer.py loss1.csv
```

### Step 4️⃣ – Start the Flask Web App  
```bash
python app.py
```

### Step 5️⃣ – Open in Browser  
```
http://127.0.0.1:5000/?file=pet_batch_output*.csv
```
- * is series number of batch data.

### Step 6️⃣ – View Help  
```bash
python pet_analyzer.py help
```

---

## 🖼️ Demo Screenshot

![Demo](https://github.com/41171119H/Data-Structure/blob/main/autogen/petLoss/petLossDemo.png)

