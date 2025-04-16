import os
import threading
import asyncio
import pandas as pd
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from EMOwithSnow import generate_mood_trend_plot
from multiagent import run_multiagent_analysis

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, async_mode='threading')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Batch size for processing
BATCH_SIZE = 10  # Adjust the batch size based on your needs

def process_batch(file_path, batch_start, batch_end):
    try:
        df = pd.read_csv(file_path)
        batch_data = df.iloc[batch_start:batch_end]
        user_id = os.path.splitext(os.path.basename(file_path))[0]

        # Generate mood trend plot for this batch
        plot_path = generate_mood_trend_plot(user_id, batch_data)
        socketio.emit('plot_generated', {'plot_url': '/' + plot_path})

        # Process the batch using multi-agent analysis
        asyncio.run(run_multiagent_analysis(socketio, user_id, batch_data))

    except Exception as e:
        socketio.emit('update', {'message': f"❌ 分析過程出現錯誤: {str(e)}"})

def batch_analysis(file_path):
    df = pd.read_csv(file_path)
    total_rows = len(df)

    # Loop through the data in batches
    for i in range(0, total_rows, BATCH_SIZE):
        batch_start = i
        batch_end = min(i + BATCH_SIZE, total_rows)
        thread = threading.Thread(target=process_batch, args=(file_path, batch_start, batch_end))
        thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        socketio.emit('update', {'message': '🟢 檔案上傳成功，開始分析中...'})
        # Start batch processing
        threading.Thread(target=batch_analysis, args=(file_path,)).start()
        return 'File uploaded and processing started.', 200

if __name__ == '__main__':
    socketio.run(app, debug=True)
