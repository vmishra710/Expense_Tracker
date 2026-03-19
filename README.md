---

# 💸 Expense Tracker API

A secure, modular, and scalable backend API built with FastAPI to help users manage and analyze their personal expenses. This project demonstrates authentication, CRUD operations, SQL aggregation, and raw query handling—all wrapped in clean architecture.

Deployed = https://expense-tracker-i4jj.onrender.com

---

## 🚀 Features

- 🔐 JWT-based user authentication
- 👤 User registration and login
- 💰 CRUD operations for Expenses
- 🔄 Pagination with metadata
- 🧱 Dependency injection for clean code
- 🔒 Secure password hashing with bcrypt
- 📅 Filter expenses by date range
- 📊 View top N spending categories
- 📈 Category-wise expense summaries
- 🧠 Raw SQL queries for performance and flexibility

---

## 🧱 Tech Stack

- **FastAPI** – High-performance Python web framework
- **SQLAlchemy** – ORM for database modeling
- **PostgreSQL** – Relational database
- **Pydantic** – Data validation and serialization
- **bcrypt** – Secure password hashing
- **JWT (python-jose)** – Token-based authentication

---

## 📁 Project Structure

```
Expense_Tracker/
├── routers/            # Modular route handlers (auth, expenses)
├── models.py           # SQLAlchemy models
├── database.py         # DB connection and session
├── dependencies.py     # Dependency injection setup
├── security.py         # Password hashing and token logic
├── config.py           # Configuration settings
├── main.py             # FastAPI app entry point
├── pagination.py       # Pagination utility with metadata
```

---

## 📦 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/vmishra710/Expense_Tracker.git
   cd Expense_Tracker
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   ```

3. Set up your PostgreSQL database and update `config.py` or `.env` with your DB credentials.

4. Run the app:
   ```bash
   uvicorn main:app --reload
   ```

---

## 🔍 API Endpoints

| Method | Endpoint               | Description                          |
|--------|------------------------|--------------------------------------|
| POST   | `/auth/register`       | Register a new user                  |
| POST   | `/auth/token`          | Login and receive JWT token          |
| GET    | `/expenses/`           | List all expenses                    |
| POST   | `/expenses/`           | Create a new expense                 |
| PUT    | `/expenses/{id}`       | Update an expense                    |
| DELETE | `/expenses/{id}`       | Delete an expense                    |
| GET    | `/expenses/summary`    | View category-wise expense summary   |
| GET    | `/expenses/filter`     | Filter expenses by date range        |
| GET    | `/expenses/top-categories` | View top N spending categories   |

---

## 👤 Author

**Vaibhav Mishra**  
Backend Developer | Python & FastAPI Enthusiast  
[GitHub Profile](https://github.com/vmishra710)
