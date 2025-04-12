import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
import google.generativeai as genai
import re
import warnings
warnings.filterwarnings("ignore", message="cmap value too big/small:*")

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def get_chinese_font_file() -> str:
    fonts_path = r"C:\\Windows\\Fonts"
    candidates = ["kaiu.ttf"]
    for font in candidates:
        font_path = os.path.join(fonts_path, font)
        if os.path.exists(font_path):
            print("找到系統中文字型：", font_path)
            return os.path.abspath(font_path)
    print("未在系統中找到候選中文字型檔案。")
    return None

def create_table(pdf: FPDF, df: pd.DataFrame):
    available_width = pdf.w - 2 * pdf.l_margin
    cell_height = 8
    font_size = 9
    pdf.set_font("ChineseFont", size=font_size)

    col_widths = []
    for col in df.columns:
        if "留言" in col or "關鍵詞" in col:
            col_widths.append(available_width * 0.45)
        else:
            col_widths.append(available_width * 0.55 / (len(df.columns) - 1))

    scale = available_width / sum(col_widths)
    col_widths = [w * scale for w in col_widths]

    pdf.set_fill_color(200, 200, 200)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], cell_height, str(col), border=1, align="C", fill=True)
    pdf.ln(cell_height)

    fill = False
    for index, row in df.iterrows():
        if pdf.get_y() + cell_height > pdf.h - pdf.b_margin:
            pdf.add_page()
            pdf.set_fill_color(200, 200, 200)
            for i, col in enumerate(df.columns):
                pdf.cell(col_widths[i], cell_height, str(col), border=1, align="C", fill=True)
            pdf.ln(cell_height)

        pdf.set_fill_color(245, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        max_lines = 1
        cell_texts = [str(item).replace("**", "") for item in row]

        for i, text in enumerate(cell_texts):
            lines = pdf.multi_cell(col_widths[i], cell_height, text, border=0, align="L", split_only=True)
            if len(lines) > max_lines:
                max_lines = len(lines)

        y_start = pdf.get_y()
        for i, text in enumerate(cell_texts):
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.set_xy(x, y)
            pdf.multi_cell(col_widths[i], cell_height, text, border=1, align="L", fill=True)
            pdf.set_xy(x + col_widths[i], y)

        pdf.set_y(y_start + max_lines * cell_height)
        fill = not fill

def parse_markdown_table(markdown_text: str) -> pd.DataFrame:
    lines = markdown_text.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines:
        return None
    header_line = table_lines[0]
    headers = [h.strip() for h in header_line.strip("|").split("|")]
    data = []
    for line in table_lines[2:]:
        row = [cell.strip() for cell in line.strip("|").split("|")]
        if len(row) == len(headers):
            data.append(row)
    df = pd.DataFrame(data, columns=headers)
    return df

def generate_pdf(text: str = None, df: pd.DataFrame = None) -> str:
    print("開始生成 PDF")
    pdf = FPDF(format="A4")
    pdf.add_page()

    chinese_font_path = get_chinese_font_file()
    if not chinese_font_path:
        return "錯誤：無法取得中文字型檔"

    pdf.add_font("ChineseFont", "", chinese_font_path, uni=True)
    pdf.set_font("ChineseFont", "", 12)

    if df is not None:
        create_table(pdf, df)
    elif text is not None:
        if "|" in text:
            table_part = "\n".join([line for line in text.splitlines() if line.strip().startswith("|")])
            parsed_df = parse_markdown_table(table_part)
            if parsed_df is not None:
                create_table(pdf, parsed_df)
            else:
                pdf.multi_cell(0, 10, text)
        else:
            pdf.multi_cell(0, 10, text)
    else:
        pdf.cell(0, 10, "沒有可呈現的內容")

    output_dir = "pdf_report"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(filename)
    print("PDF 已儲存：", filename)
    return filename

def gradio_handler(csv_file, user_prompt):
    print("進入 gradio_handler")
    if csv_file is not None:
        print("讀取 CSV 檔案")
        df = pd.read_csv(csv_file.name)
        total_rows = df.shape[0]
        block_size = 30
        cumulative_response = ""
        for i in range(0, total_rows, block_size):
            block = df.iloc[i:i+block_size]
            block_csv = block.to_csv(index=False)
            prompt = (f"以下是CSV資料第 {i+1} 到 {min(i+block_size, total_rows)} 筆：\n"
                      f"{block_csv}\n\n請根據以下規則進行分析並產出報表：\n{user_prompt}")
            print("完整 prompt for block:")
            print(prompt)
            response = model.generate_content(prompt)
            block_response = response.text.strip()
            cumulative_response += f"區塊 {i//block_size+1}:\n{block_response}\n\n"

        pdf_path = generate_pdf(text=cumulative_response)
        return cumulative_response, pdf_path
    else:
        context = "未上傳 CSV 檔案。"
        full_prompt = f"{context}\n\n{user_prompt}"
        print("完整 prompt：")
        print(full_prompt)
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        print("AI 回應：")
        print(response_text)
        pdf_path = generate_pdf(text=response_text)
        return response_text, pdf_path

default_prompt = """請針對每筆留言進行以下分析：
1. 對每則留言判斷情緒傾向（正向、中立、負向）與關鍵字（如：服務、價格、洗澡、環境、客服、商品）
2. 統計所有關鍵字的出現次數，並列出情緒傾向與關鍵字的交叉分析（例如「洗澡」在正向出現幾次、負向幾次）
3. 發現出現頻率最高的關鍵字與負面關鍵字，並分析這些詞的共通點（例如：哪些負評反覆提到「服務不好」或「電話打不通」）
4. 給出具體的改善建議，例如哪些方面最常被抱怨，店家可以優先改進什麼，或是哪些優點可以強化作為行銷亮點
5. 最後請總結：整體顧客情緒傾向如何？（例如：「整體顧客以正向居多，但部分服務流程與聯絡方式造成顧客不滿。」）
"""

with gr.Blocks() as demo:
    gr.Markdown("# 寵物店留言統整，由CSV檔案分析")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.Textbox(label="回應內容", interactive=False)
    output_pdf = gr.File(label="下載 PDF 報表")
    submit_button = gr.Button("生成報表")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()