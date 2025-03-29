# Lost Pet Dataset Analysis & Search Platform

## 📁 Data Description

This project uses a dataset of reported lost pets in CSV format, named `petLoss.csv`. Each record contains the following fields:

- Chip number  
- Pet name  
- Pet type and sex  
- Breed  
- Color  
- Appearance / Features  
- Lost time and location  
- Owner name and contact info  
- Picture URL (if any)

---

## 🤖 `pet_analyzer.py` Script Key Points

### Analysis Items (ITEMS)

- Is the lost location specific?  
- Does it contain recognizable color features?  
- Is the feature/appearance description clear?  
- Is the lost time clearly defined?  
- Is the information suitable for public notice?  
- Suggestions for improving report completeness  
- Is there a photo provided?

### Prompt Logic

Each batch of records is sent to the Gemini API with an instruction to analyze the fields above and return structured CSV responses per item.

### Input/Output Files

- Input: `petLoss.csv` or split files like `loss1.csv`, `loss2.csv`, etc.  
- Output: `pet_batch_output1.csv`, `pet_batch_output2.csv`, etc., each with Gemini analysis results

---

## 🌐 Flask Web Interface

- The web backend is implemented using `app.py`
- Default route `/` loads the web page
- Specify the file to display using query string, e.g. `?file=pet_batch_output1.csv`
- Automatically merges with the corresponding `loss1.csv` for displaying original details
- Supports filtering by analysis fields and sorting by completeness score

---

## 🚀 How to Use

```bash
# 1. Split the main dataset into 1000-record chunks
python pet_analyzer.py split

# 2. Analyze all split files automatically
python pet_analyzer.py

# 3. Analyze a specific file
python pet_analyzer.py loss1.csv

# 4. Start the web server
python app.py

# 5. Open your browser
http://127.0.0.1:5000/?file=pet_batch_output*.csv
- *=serial number of natch data. 

# 6. Demo Screenshot
![Demo](petLossDemo.png)

# 7. Display help instructions
python pet_analyzer.py help
