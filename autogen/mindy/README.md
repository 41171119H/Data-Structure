# MINDY - Mindful Intelligent Navigator for Daily You

MINDY is a personal self-improvement assistant that provides a dashboard for daily summaries, reminders, interview practice, study progress, and savings tracking.

---

## 📁 Project Structure

```
MINDY/
├── backend.py             # Flask backend server with API endpoints
├── mindy_dashboard.jsx    # React component for the UI dashboard
├── prototype.md           # Project planning and notes
└── README.md              # Project instructions (this file)
```

---

## ⚙️ Requirements

### Backend:
- Python 3.8+
- Flask
- Flask-CORS

### Frontend:
- Node.js v16+ (you have v20, perfect!)
- npm (you have v10+)
- React with Vite setup
- recharts (for chart rendering)

---

## 🚀 How to Run the Project

### 1. Start Backend (Flask)

```bash
cd MINDY
python -m venv venv
venv\Scripts\activate     # Windows 用戶
pip install flask flask-cors
python backend.py
```

The backend server will run at:  
📡 `http://127.0.0.1:5000`

---

### 2. Set Up Frontend (React + Vite)

```bash
npm create vite@latest mindy-dashboard -- --template react
cd mindy-dashboard
npm install
npm install recharts
```

將 `mindy_dashboard.jsx` 放到 `src/components/` 目錄下，並在 `App.jsx` 引入：

```jsx
import MindyDashboard from './components/mindy_dashboard';

function App() {
  return <MindyDashboard />;
}
```

然後執行：
```bash
npm run dev
```
開啟瀏覽器進入：  
🌐 `http://localhost:5173`

---

## 📦 Features
- 🌤 Daily AI Digest Summary
- 📝 Reminder Checklist (static for now)
- 💬 Mock Interview UI
- 📊 Study Progress BarChart
- 💰 Savings Jar with live progress

---

## 🛠️ Next Goals
- [ ] 接上 AutoGen / Gemini API 回答面試問題
- [ ] Reminders 可編輯與持久化
- [ ] 匯出 PDF 報表
- [ ] 使用者登入與個人化體驗

---

## 🧑‍💻 Author
Developed by YunZhen Yang (楊芸蓁) using Flask + React + ShadCN UI

For academic, personal growth, and full-stack portfolio development.



