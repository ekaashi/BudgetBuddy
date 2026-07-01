# 💰 Budget Buddy

Budget Buddy is a modern expense management web application built with **Flask** that helps users efficiently track, organize, and analyze their daily expenses. It provides a clean, responsive dashboard where users can add, edit, delete, and filter expenses by date and category. The application also includes interactive data visualizations using **Chart.js**, allowing users to gain insights into their spending habits through pie and line charts. Additionally, users can export filtered expense records as CSV files for reporting and backup purposes.

Built using **Python**, **Flask**, **Flask-SQLAlchemy**, **SQLite**, **Tailwind CSS**, and **Jinja2**, Budget Buddy demonstrates full-stack web development concepts including CRUD operations, database integration, form validation, template rendering, flash messaging, and responsive UI design.

---

## ✨ Features

- 💰 Add, edit, and delete expenses
- 📅 Filter expenses by date range
- 🏷️ Filter expenses by category
- 📊 Interactive Pie Chart (Category-wise Spending)
- 📈 Line Chart (Expense Trend Over Time)
- 💵 Automatic total expense calculation
- 📄 Export filtered expenses to CSV
- 🔔 Flash messages for user feedback
- 📱 Responsive and modern UI using Tailwind CSS
- 🗄️ SQLite database integration with SQLAlchemy ORM

---

## 🛠️ Tech Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy

**Frontend**
- HTML5
- Jinja2
- Tailwind CSS
- Chart.js

**Database**
- SQLite

---

## 🚀 Installation

```bash
git clone https://github.com/ekaashi/budget-buddy.git

cd budget-buddy

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
Budget-Buddy/
│
├── app.py
├── requirements.txt
├── expenses.db
│
├── templates/
│   ├── base.html
│   ├── index.html
│   └── edit.html
│
├── static/
│
└── README.md
```

---

## 🔮 Future Improvements

- 🔐 User Authentication
- 📄 PDF & Excel Export
- 📅 Monthly Budget Planning
- 🌙 Dark/Light Mode
- ☁️ Cloud Database Integration
- 📊 Advanced Analytics & Reports
- 📱 Progressive Web App (PWA)

---

## 👨‍💻 Author

**Abhishek Rajpoot**

B.Tech – Artificial Intelligence & Data Science

GitHub: https://github.com/ekaashi

---

⭐ If you like this project, consider giving it a **Star** on GitHub!
