# 🛒 E-Commerce Backend & Concurrency Services

> **Production-grade E-Commerce Backend built with FastAPI, PostgreSQL, Redis, and AWS EC2.**

<p *align*="center">


![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-Enabled-red)
![AWS](https://img.shields.io/badge/AWS-EC2-orange)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-success)
![Gunicorn](https://img.shields.io/badge/Gunicorn-WSGI-darkgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

</p>

---

# 📖 Overview

A production-oriented backend for an e-commerce platform built using **FastAPI**.

The project goes beyond basic CRUD operations and demonstrates backend engineering concepts including authentication, role-based authorization, transactional integrity, concurrency control, Redis caching, automated testing, CI/CD, and cloud deployment.

---

# ✨ Features

* JWT Authentication
* Role-Based Access Control (Admin / Customer)
* Secure Password Hashing (bcrypt)
* Product Management
* Category Management
* Inventory Management
* Shopping Cart
* Checkout System
* Product Reviews
* PostgreSQL Transactions
* Row-Level Locking (`SELECT ... FOR UPDATE`)
* Redis Caching
* Alembic Database Migrations
* Automated Testing with Pytest
* GitHub Actions CI/CD
* AWS EC2 Deployment
* Gunicorn + Uvicorn Workers
* Nginx Reverse Proxy
* Systemd Service Management

---

# 🏗️ Production Architecture

```text
                    Internet
                        │
                        ▼
              ┌────────────────┐
              │     Nginx      │
              │ Reverse Proxy  │
              └───────┬────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Gunicorn Master  │
             └───────┬──────────┘
             ┌───────┴──────────┐
             ▼                  ▼
      Uvicorn Worker      Uvicorn Worker
             └───────┬──────────┘
                     ▼
                  FastAPI
              ┌──────┴──────┐
              ▼             ▼
         PostgreSQL       Redis
```

---

# 🧰 Tech Stack

| Layer               | Technology         |
| ------------------- | ------------------ |
| Language            | Python 3.12        |
| Framework           | FastAPI            |
| ORM                 | SQLAlchemy         |
| Database            | PostgreSQL         |
| Cache               | Redis              |
| Authentication      | JWT                |
| Password Hashing    | bcrypt             |
| Database Migrations | Alembic            |
| Testing             | Pytest             |
| CI/CD               | GitHub Actions     |
| Reverse Proxy       | Nginx              |
| Application Server  | Gunicorn + Uvicorn |
| Service Manager     | Systemd            |
| Cloud               | AWS EC2            |

---

# 📂 Project Structure

```text
app/
├── core/
│   └── redis.py
├── routers/
│   ├── auth.py
│   ├── product.py
│   ├── category.py
│   ├── cart.py
│   └── checkout.py
├── auth.py
├── database.py
├── models.py
├── schemas.py
└── main.py

alembic/
tests/

requirements.txt
README.md
```

---

# 🗄️ Database Design

```text
Users
 │
 ├──────────────┐
 ▼              ▼
Orders       CartItems
 │              │
 ▼              │
OrderItems      │
 │              │
 └──────► Products ◄──── Reviews
             │
             ▼
         Categories
             │
             ▼
        Inventories
```

---

# 🔐 Authentication Flow

```text
Register/Login
      │
      ▼
Password Verification
      │
      ▼
JWT Generation
      │
      ▼
Client Stores Token
      │
      ▼
Authorization Header
      │
      ▼
Protected API Endpoints
```

---

# ⚡ Transactional Checkout

The checkout system guarantees ACID compliance.

```text
Start Transaction
        │
        ▼
Lock Inventory Row
        │
        ▼
Validate Stock
        │
        ▼
Create Order
        │
        ▼
Create Order Items
        │
        ▼
Reduce Inventory
        │
        ▼
Clear Shopping Cart
        │
        ▼
Commit Transaction
```

If any step fails, the transaction is rolled back automatically.

---

# 🚦 Concurrency Control

Overselling is prevented using PostgreSQL row-level locking.

```python
inventory = (
    db.query(Inventory)
      .filter(Inventory.product_id == item.product_id)
      .with_for_update()
      .first()
)
```

Generated SQL:

```sql
SELECT *
FROM inventories
WHERE product_id = ?
FOR UPDATE;
```

This guarantees that concurrent purchases cannot modify the same inventory row simultaneously.

---

# ⚡ Redis Integration

Redis is used as a high-speed in-memory cache to reduce database load and improve API response time.

Current implementation:

* Product list caching
* Automatic cache invalidation after product updates

The architecture is ready to support:

* Rate limiting
* Session storage
* Background jobs
* Queue processing

---

# 📡 API Modules

| Module         | Description            |
| -------------- | ---------------------- |
| Authentication | Register & Login       |
| Products       | CRUD Operations        |
| Categories     | CRUD Operations        |
| Inventory      | Stock Management       |
| Cart           | Shopping Cart          |
| Checkout       | Transaction Processing |
| Reviews        | Product Reviews        |

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 🧪 Automated Testing

The project includes automated tests using **Pytest**.

Current test coverage includes:

* Authentication
* JWT Authorization
* RBAC
* Categories
* Products
* Inventory
* Shopping Cart
* Checkout Transactions
* Order Creation

Run locally:

```bash
pytest -v
```

---

# 🔄 CI/CD Pipeline

Every push to the **main** branch automatically triggers GitHub Actions.

Pipeline:

```text
Developer
      │
      ▼
git push
      │
      ▼
GitHub Actions
      │
      ▼
Checkout Repository
      │
      ▼
Install Dependencies
      │
      ▼
Ruff Linting
      │
      ▼
Black Formatting Check
      │
      ▼
Pytest
      │
      ▼
SSH into AWS EC2
      │
      ▼
Pull Latest Code
      │
      ▼
Install Dependencies
      │
      ▼
Alembic Migration
      │
      ▼
Restart Redis
      │
      ▼
Restart FastAPI
      │
      ▼
Deployment Complete
```

---

# ☁️ Production Deployment

Deployed on **Ubuntu AWS EC2** using:

* FastAPI
* Gunicorn
* Uvicorn Workers
* Nginx
* PostgreSQL
* Redis
* Systemd
* GitHub Actions

Deployment architecture:

```text
Developer
    │
git push
    │
GitHub Actions
    │
SSH
    │
AWS EC2
    │
git pull
    │
pip install
    │
alembic upgrade head
    │
Restart Services
    │
Nginx
    │
Users
```

---

# 🚀 Local Setup

Clone the repository:

```bash
git clone https://github.com/Turbocyborg/E-Commerce-Backend-Concurrency-Services.git

cd E-Commerce-Backend-Concurrency-Services
```

Create a virtual environment:

```bash
python -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/ecommerce
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379/0
```

Run migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn app.main:app --reload
```

---

# 🔒 Security

* JWT Authentication
* Password Hashing (bcrypt)
* Role-Based Access Control
* Environment Variables
* SQLAlchemy ORM
* Protected Admin Routes
* Transaction Rollback Protection

---

# 🧠 Engineering Concepts Demonstrated

* REST API Design
* Dependency Injection
* ACID Transactions
* Concurrency Control
* Row-Level Locking
* Database Normalization
* SQLAlchemy ORM
* Redis Caching
* Automated Testing
* Continuous Integration
* Continuous Deployment
* Linux Service Management
* Cloud Deployment

---

# 📚 What I Learned

Through this project I gained practical experience with:

* Designing scalable REST APIs using FastAPI
* Implementing JWT authentication and RBAC
* Managing SQLAlchemy relationships
* Building transactional database operations
* Preventing race conditions using PostgreSQL row-level locking
* Integrating Redis for caching
* Writing automated tests with Pytest
* Building CI/CD pipelines using GitHub Actions
* Deploying production applications on AWS EC2
* Managing Gunicorn, Nginx, Redis, and Systemd services

---

# 🛣️ Future Improvements

* Docker
* Docker Compose
* Kubernetes
* AWS RDS
* AWS S3 Product Images
* Celery Background Tasks
* Prometheus Monitoring
* Grafana Dashboards
* Elasticsearch

---

# 📸 Screenshots

## Add screenshots here:

- Swagger UI

   ![alt text](image.png)


- PostgreSQL Tables

   ![alt text](image-1.png)


- EC2 Deployment

   ![alt text](image-2.png)


- API Responses

   ![alt text](image-3.png)

   ![alt text](image-4.png)

---

# 🌐 Live API

Swagger UI

```text
http://13.60.232.161/docs
```

---

# 👨‍💻 Author

## Prateek Kumar Yadav

Backend Engineer | Python | FastAPI | PostgreSQL | Redis | AWS

---

⭐ If you found this project useful, consider giving it a star.
