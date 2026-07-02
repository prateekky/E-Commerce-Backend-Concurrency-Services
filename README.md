
# 🛒 E-Commerce Backend Engine
> **Production-grade E-Commerce Backend built with FastAPI, PostgreSQL, Redis and AWS EC2**

<p align="center">

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

## 📖 Overview

This project is a production-oriented backend for an e-commerce platform. Beyond CRUD operations, it demonstrates **authentication, authorization, ACID transactions, concurrency control, caching, database migrations, and Linux deployment**.

---

# ✨ Key Features

- JWT Authentication
- Role-Based Access Control (Admin / Customer)
- Secure Password Hashing (Bcrypt)
- Product & Category Management
- Shopping Cart
- Inventory Management
- Order Processing
- Product Reviews
- Redis Integration
- PostgreSQL Transactions
- Row-Level Locking (`SELECT ... FOR UPDATE`)
- Alembic Database Versioning
- AWS EC2 Deployment
- Nginx Reverse Proxy
- Gunicorn + Uvicorn Workers
- Systemd Service Management

---

# 🏗️ Production Architecture

```text
                    Internet
                        │
                        ▼
                  ┌───────────┐
                  │   Nginx   │
                  └─────┬─────┘
                        │
                        ▼
               ┌────────────────┐
               │ Gunicorn Master│
               └──────┬─────────┘
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     Uvicorn      Uvicorn     Uvicorn
      Worker        Worker       Worker
          └──────────┬───────────┘
                     ▼
                  FastAPI
              ┌──────┴──────┐
              ▼             ▼
          PostgreSQL      Redis
```

---

# 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Cache | Redis |
| Migrations | Alembic |
| Auth | JWT |
| Hashing | Bcrypt |
| Reverse Proxy | Nginx |
| Process Manager | Gunicorn |
| Service Manager | Systemd |
| Cloud | AWS EC2 |

---

# 📂 Folder Structure

```text
app/
├── routers/
├── models.py
├── schemas.py
├── auth.py
├── dependencies.py
├── database.py
├── redis_client.py
└── main.py

alembic/
└── versions/

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

Products
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
Password Verified
      │
      ▼
JWT Generated
      │
      ▼
Client Stores Token
      │
      ▼
Authorization Header
      │
      ▼
Protected Endpoints
```

---

# ⚡ Checkout Transaction

```text
Start Transaction
        │
Lock Inventory Row
        │
Check Stock
        │
Create Order
        │
Create Order Items
        │
Reduce Inventory
        │
Commit
```

If any step fails, the transaction rolls back.

---

# 🚦 Concurrency Control

The checkout service prevents overselling with PostgreSQL row-level locking.

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

---

# ⚙️ Redis

Redis is used as a high-speed in-memory data store for performance-oriented operations and is ready to support caching, rate limiting, session storage, or future background processing.

---

# 📡 API Modules

| Module | Description |
|---|---|
| Authentication | Register & Login |
| Products | CRUD |
| Categories | CRUD |
| Inventory | Stock Updates |
| Cart | User Shopping Cart |
| Checkout | Transactional Purchase |
| Orders | Order History |
| Reviews | Ratings & Feedback |

Swagger:

```text
http://localhost:8000/docs
```

---

# ☁️ Deployment

Deployed on Ubuntu AWS EC2 using:

- FastAPI
- Gunicorn
- Uvicorn Workers
- Nginx
- PostgreSQL
- Redis
- Systemd

Deployment flow:

```text
GitHub
   │
git pull
   │
pip install
   │
alembic upgrade head
   │
systemctl restart fastapi
   │
Nginx
   │
Users
```

---

# 🚀 Local Setup

```bash
git clone https://github.com/Turbocyborg/E-Commerce-Backend-Concurrency-Services.git
cd E-Commerce-Backend-Concurrency-Services

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env`

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/ecommerce
SECRET_KEY=your_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

Run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

---

# 🔒 Security

- JWT Authentication
- Bcrypt Password Hashing
- RBAC
- SQLAlchemy ORM
- Environment Variables
- Protected Admin Routes

---

# 🧠 Engineering Concepts

- REST API Design
- Dependency Injection
- ACID Transactions
- Database Normalization
- Row-Level Locking
- Concurrency Control
- ORM Optimization
- Redis Integration
- Production Deployment
- Linux Administration

---

# 🛣️ Future Roadmap

- Docker Compose
- GitHub Actions CI/CD
- Celery
- Prometheus + Grafana
- Kubernetes
- AWS RDS
- S3 Product Images
- Elasticsearch

---

# 📸 Screenshots

Add screenshots here:

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

# 👨‍💻 Author

## Prateek Kumar Yadav

Backend Engineer | Python | FastAPI | PostgreSQL | Redis | AWS

**Live API**

`http://13.60.232.161/docs`

---

⭐ If you found this project useful, consider giving it a star.
