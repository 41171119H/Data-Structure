import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
from google import genai

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_pdf(text: str = None, df: pd.DataFrame = None) -> str:
    print("Generating PDF report...")
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    if df is not None:
        col_width = (pdf.w - 2 * pdf.l_margin) / len(df.columns)
        cell_height = 10

        pdf.set_fill_color(200, 200, 200)
        for col in df.columns:
            pdf.cell(col_width, cell_height, str(col), border=1, align="C", fill=True)
        pdf.ln(cell_height)

        fill = False
        for _, row in df.iterrows():
            if pdf.get_y() + cell_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                pdf.set_fill_color(200, 200, 200)
                for col in df.columns:
                    pdf.cell(col_width, cell_height, str(col), border=1, align="C", fill=True)
                pdf.ln(cell_height)
            if fill:
                pdf.set_fill_color(240, 240, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
            for item in row:
                pdf.cell(col_width, cell_height, str(item), border=1, align="C", fill=True)
            pdf.ln(cell_height)
            fill = not fill

    elif text is not None:
        pdf.multi_cell(0, 10, text)
    else:
        pdf.cell(0, 10, "No content to display.")

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    print("PDF saved as:", filename)
    return filename

def gradio_handler(csv_file, user_prompt):
    print("Handling Gradio input...")
    if csv_file is not None:
        df = pd.read_csv(csv_file.name)
        total_rows = df.shape[0]
        block_size = 30
        combined_response = ""

        for i in range(0, total_rows, block_size):
            block = df.iloc[i:i+block_size]
            block_csv = block.to_csv(index=False)
            prompt = f"""Here are customer feedback entries {i+1} to {min(i+block_size, total_rows)}:
{block_csv}

Follow the instructions below:
{user_prompt}"""
            print("Prompt for block", i//block_size+1)
            response = client.models.generate_content(
                model="gemini-2.5-pro-exp-03-25",
                contents=[prompt]
            )
            block_text = response.text.strip()
            combined_response += f"Block {i//block_size+1} Analysis:\n{block_text}\n\n"

        pdf_path = generate_pdf(text=combined_response)
        return combined_response, pdf_path
    else:
        full_prompt = f"No CSV uploaded. Use this prompt directly:\n\n{user_prompt}"
        response = client.models.generate_content(
            model="gemini-2.5-pro-exp-03-25",
            contents=[full_prompt]
        )
        text = response.text.strip()
        pdf_path = generate_pdf(text=text)
        return text, pdf_path

# Default English prompt for analysis
default_prompt = """Please analyze each customer review based on the following instructions:

1. Classify the sentiment as Positive, Neutral, or Negative.
2. Extract important keywords from each review (e.g., service, price, bath, grooming, staff, products).
3. Count how many reviews fall into each sentiment category, and show percentages.
4. Create a frequency list of keywords and show the top 10 most common ones.
5. Finally, write a short summary paragraph (about 100-150 words) that describes customer impressions and areas for improvement.

Output should be in clear English with structured formatting such as headings or tables if necessary.
"""

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Pet Store Feedback Report Generator")
    with gr.Row():
        csv_input = gr.File(label="Upload CSV File")
        user_input = gr.Textbox(label="Enter Analysis Instructions", lines=10, value=default_prompt)
    output_text = gr.Textbox(label="AI Analysis Output", interactive=False)
    output_pdf = gr.File(label="Download PDF Report")
    submit_button = gr.Button("Generate Report")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
