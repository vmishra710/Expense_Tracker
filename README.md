# 💸 Expense Tracker API (Production-Ready Backend)

A **production-grade backend system** built with FastAPI to manage and analyze personal expenses.

This project goes beyond CRUD and demonstrates:

* 🔥 **Distributed system design**
* ⚡ **Async + background processing**
* 🧠 **Real-world debugging & deployment**

---

## 🌐 Live Deployment

👉 https://expense-tracker-i4jj.onrender.com

> ⚠️ Note: Free tier may take ~30–50 seconds to wake up.

---

## 🚀 Features

### 🔐 Authentication & Security

* JWT-based authentication (login/register)
* Secure password hashing (bcrypt)
* Role-based access (admin/user)

---

### 💰 Expense Management

* Create, update, delete expenses
* Filter by date range
* Pagination with metadata
* Category-wise summaries
* Top spending categories

---

### ⚡ Background Processing (Celery)

* Monthly expense report generation
* Email sending in background
* Non-blocking API execution

---

### 📊 Advanced Features

* Async database support
* Optimized queries (joins, aggregation)
* Lazy vs eager loading (performance)

---

## 🧠 System Architecture

```
User Request
    ↓
FastAPI (API Layer)
    ↓
PostgreSQL (Database)
    ↓
Redis (Queue / Broker)
    ↓
Celery Worker (Background Tasks)
    ↓
Email Service (SMTP)
```

---

## 🧱 Tech Stack

### Backend

* **FastAPI** – High-performance async framework
* **SQLAlchemy** – ORM (sync + async)
* **PostgreSQL** – Relational database

### Background Processing

* **Celery** – Task queue system
* **Redis (Upstash)** – Broker + result backend

### DevOps

* **Docker & Docker Compose** – Multi-service setup
* **Render** – API + Database hosting

### Security

* **JWT (python-jose)** – Authentication
* **bcrypt / passlib** – Password hashing

---

## 📁 Project Structure

```
Expense_Tracker/
├── routers/                # API routes (auth, users, expenses, reports)
├── tasks/                  # Celery background tasks
├── services/               # Business logic (reports, email)
├── models.py               # SQLAlchemy models
├── database.py             # DB setup (sync + async)
├── celery_app.py           # Celery configuration
├── dependencies.py         # Dependency injection
├── security.py             # JWT + password hashing
├── middlewares/            # Logging, rate limiting
├── main.py                 # FastAPI entry point
├── Dockerfile
├── docker-compose.yml
```

---

## ⚙️ Local Setup (Docker - Recommended)

```bash
git clone https://github.com/vmishra710/Expense_Tracker.git
cd Expense_Tracker

docker-compose up --build
```

Access API:
👉 http://localhost:8000/docs

---

## 🔑 Environment Variables

Create a `.env` file:

```
DATABASE_URL=your_postgres_url
REDIS_URL=your_redis_url
EMAIL=your_email
APP_PASSWORD=your_app_password
```

---

## 🔍 Key API Endpoints

| Method | Endpoint            | Description            |
| ------ | ------------------- | ---------------------- |
| POST   | `/auth/register`    | Register user          |
| POST   | `/auth/token`       | Login                  |
| GET    | `/expenses/`        | List expenses          |
| POST   | `/expenses/`        | Create expense         |
| GET    | `/expenses/summary` | Category summary       |
| GET    | `/reports/monthly`  | Trigger monthly report |

---

## 🧠 Key Learnings (Real-World)

* Difference between **sync vs async**
* Why **Celery is needed for background tasks**
* Redis as **message broker vs cache**
* Docker for **multi-service architecture**
* Handling **production vs local environments**
* Debugging:

  * DB connection issues
  * Redis TLS errors
  * Celery worker failures
  * Env variable loading issues

---

## ⚠️ Important Notes

* Celery worker must be running for background tasks
* Redis must be accessible (Upstash in production)
* Tables auto-created using FastAPI lifespan

---

## 👨‍💻 Author

**Vaibhav Mishra**
Backend Developer | Python & FastAPI

🔗 https://github.com/vmishra710
