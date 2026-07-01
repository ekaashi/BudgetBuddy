# 💰 Budget Buddy

A lightweight personal expense tracker built with Flask, SQLite, and Tailwind CSS — with a built-in AI chatbot (powered by Groq/Llama) that lets you add, edit, and query your expenses using plain English.

![Python](https://img.shields.io/badge/python-3.9+-blue)
![Flask](https://img.shields.io/badge/flask-backend-black)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **Track expenses** — add, edit, and delete expenses with a description, amount, category, and date.
- **Filter & search** — filter the dashboard by date range and category.
- **Visual insights** — interactive pie chart (spend by category) and line chart (spend over time), powered by Chart.js.
- **CSV export** — export the currently filtered expenses to a CSV file.
- **AI chatbot assistant** — a floating chat widget lets you manage expenses conversationally:
  - *"spent 450 on groceries yesterday"* → logs the expense automatically
  - *"how much did I spend on food this month?"* → summarizes your spending
  - *"delete the coffee expense from Tuesday"* → finds and removes it (asks for clarification if there's more than one match)
- **Clean dark UI** — polished dark theme built with Tailwind CSS.

---

## 🛠 Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Flask, Flask-SQLAlchemy, SQLite      |
| Frontend   | Jinja2 templates, Tailwind CSS (CDN), Chart.js |
| AI         | Groq API (Llama 3.3, function/tool calling) |
| Config     | python-dotenv (`.env`)               |

---

## 📁 Project Structure

```
.
├── app.py                  # Flask app: routes, models, AI chat endpoint
├── templates/
│   ├── base.html           # Shared layout, nav, flash messages, chat widget
│   ├── index.html          # Dashboard: filters, add form, table, charts
│   └── edit.html           # Edit-expense form
├── .env.example            # Template for required environment variables
├── .gitignore
└── expenses.db             # SQLite database (auto-created on first run)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com/keys) (free tier available) — only needed for the AI chatbot; the rest of the app works without it.

### Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd budget-buddy

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install flask flask_sqlalchemy python-dotenv groq

# 4. Set up your environment variables
cp .env.example .env
# then edit .env and fill in:
#   GROQ_API_KEY=your_groq_api_key_here
#   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">

# 5. Run the app
python app.py
```

The app will be available at **http://127.0.0.1:5000**. The SQLite database (`expenses.db`) and its tables are created automatically on first run.

---

## ⚙️ Environment Variables

| Variable        | Required | Description                                              |
|-----------------|----------|------------------------------------------------------------|
| `GROQ_API_KEY`  | Optional | Enables the AI chatbot. Without it, the chatbot replies with a "not configured" message but the rest of the app works normally. |
| `GROQ_MODEL`    | Optional | Overrides the default model (`llama-3.3-70b-versatile`). Must support tool/function calling. |
| `SECRET_KEY`    | Recommended | Used to sign sessions and flash messages. If omitted, a random key is generated on every restart (flash messages/sessions won't persist across restarts). |

---

## 🤖 Using the AI Chatbot

Click the 💬 button in the bottom-right corner on any page. The assistant can:

- **Add expenses** from natural language ("paid 1200 for rent on the 1st")
- **Summarize spending** ("what's my total for June?", "how much on transport this week?")
- **Edit or delete expenses** by describing them (it will ask which one you mean if it's ambiguous)

Conversation history is kept in your browser's session storage, so it persists across page reloads but clears when the tab is closed. Use the 🗑 icon in the chat panel to reset the conversation at any time.

---

## 📡 API Endpoints

| Method | Route                | Description                                  |
|--------|-----------------------|-----------------------------------------------|
| GET    | `/`                    | Dashboard — filters, totals, charts, table     |
| POST   | `/add`                 | Add a new expense                             |
| POST   | `/delete/<id>`         | Delete an expense                             |
| GET/POST | `/edit/<id>`         | View/update an expense                        |
| GET    | `/export.csv`          | Export filtered expenses as CSV               |
| POST   | `/api/chat`            | AI chatbot endpoint (used by the chat widget) |

---

## 📝 License

MIT — feel free to use, modify, and share.
