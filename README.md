# 💰 Financial Record Management System

A secure and robust backend system for personal or organizational financial tracking, built with Django and Django Rest Framework.

## 🌟 Key Features

- **Standard Features**:
  - Full CRUD operations for financial records (Income/Expense).
  - Categorization and tagging of transactions.
  - Date-based tracking and notes.
- **Advanced Dashboard Analytics**:
  - `Summary`: Real-time calculation of total income, expenses, and net balance.
  - `Category Breakdown`: Visual-ready data for category-wise spending.
  - `Monthly Trends`: Time-series data for financial performance over months.
  - `Recent Activity`: Quick view of the latest 10 transactions.
- **Security & RBAC**:
  - **Role-Based Access Control** (Admin, Analyst, Viewer).
  - **Data Isolation**: Users only see their own data by default.
  - **JWT Authentication**: Secure stateless authentication using `SimpleJWT`.
- **API Documentation**: Interactive documentation via **Swagger UI** and **Redoc**.

## 🛠️ Technology Stack

- **Framework**: Django 5.x + Django Rest Framework
- **Database**: SQLite (Development) / Ready for PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: drf-spectacular (OpenAPI 3.0)

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Pip & Virtualenv

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/DevShah-09/Financial_Record_Management.git
cd Financial_Record_Management

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### 3. Seed Data
Populate the database with test users and sample records:
```bash
python manage.py seed_finance_data
```

### 4. Run the Server
```bash
python manage.py run server
```

## 🔐 Credentials (Seed Data)
- **Admin**: `admin_user` / `Password123!`
- **Analyst**: `analyst_user` / `Password123!`
- **Viewer**: `viewer_user` / `Password123!`

## 📖 API Documentation
Once the server is running, visit:
- **Swagger UI**: `/api/schema/swagger-ui/`
- **Redoc**: `/api/schema/redoc/`

---
*Developed as a secure financial management solution.*
