# MINDY - Mindful Intelligent Navigator for Daily You

MINDY is a personal self-improvement assistant that offers a daily dashboard combining AI-powered interview practice, study tracking, reminders, savings goals, and digest summaries.

---

## 🌐 Project Structure

```
/mindy
├── mindy_dashboard.jsx       # Frontend React Dashboard (ShadCN + Recharts)
├── mindy_backend.py          # Flask backend API with mock data
└── README.md                 # This instruction file
```

---

## 🚀 How to Run the Project

### 1. Backend Setup (Flask)

#### Requirements:
- Python 3.8+
- Flask
- Flask-CORS

#### Installation:
```bash
cd mindy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask flask-cors
```

#### Run Backend:
```bash
python mindy_backend.py
```
> The Flask server will run at `http://127.0.0.1:5000`

---

### 2. Frontend Setup (React + Vite or Next.js)

#### Requirements:
- Node.js (v16+ recommended)
- pnpm / npm / yarn

#### Steps:
If you already have a React project, place `mindy_dashboard.jsx` inside your pages or components folder. Otherwise, create a new project:

```bash
npm create vite@latest mindy-dashboard -- --template react
cd mindy-dashboard
npm install
```

#### Add ShadCN UI + Tailwind:
Follow setup guide at https://ui.shadcn.dev/docs/installation/react

#### Add Required Libraries:
```bash
npm install recharts
```

#### Replace or import `MindyDashboard`:
Place `mindy_dashboard.jsx` in your `src/components` and render it in `App.jsx` or your route file.

#### Run Frontend:
```bash
npm run dev
```
> React app will run at `http://localhost:5173` or similar

---

## 🧠 Features
- Daily News Summary using mock API
- Editable Reminder Checklist
- AI Interview Practice UI
- Visualized Study Progress Chart
- Savings Goal Progress with live update

---

## 📦 Next Steps
- Add connection to real AI (e.g., Gemini or OpenAI API)
- Persist data to a database
- Add login / profile system
- Export daily report to PDF

---

## 🧑‍💻 Author
Created by [Your Name] - AI dashboard project for personal development

---

Feel free to customize and extend MINDY as your personal life assistant!

