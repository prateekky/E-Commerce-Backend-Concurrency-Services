# 🛒 E-Commerce Backend Engine — FastAPI + PostgreSQL

A production-grade e-commerce backend designed to demonstrate real-world backend engineering principles including secure authentication, role-based authorization, transactional consistency, database concurrency control, and scalable deployment architecture.

Built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Alembic**, this project simulates the core infrastructure powering modern online retail systems while emphasizing correctness under concurrent workloads.

---

## 🚀 Highlights

### Secure Authentication & Authorization

* JWT-based stateless authentication
* Bcrypt password hashing
* Role-Based Access Control (RBAC)
* Protected Admin and Customer routes
* Dependency-injected permission guards

### Inventory & Order Management

* Product catalog management
* Inventory tracking
* Shopping cart functionality
* Order creation and history
* Product reviews and ratings

### ACID-Compliant Checkout Engine

The checkout workflow is implemented as a single database transaction to guarantee:

* Atomicity
* Consistency
* Isolation
* Durability

Failed operations automatically trigger transaction rollbacks, ensuring no partial orders or inventory corruption.

### Concurrency-Safe Inventory Updates

A pessimistic locking strategy is implemented using PostgreSQL row-level locks:

```python
.with_for_update()
```

This prevents overselling when multiple customers attempt to purchase the same product simultaneously.

### Optimized Database Access

* SQLAlchemy ORM
* Eager loading using `joinedload`
* Prevention of N+1 query issues
* Efficient relational querying

### Production Deployment Ready

Designed for deployment behind:

* Nginx
* Gunicorn
* Uvicorn Workers
* PostgreSQL

---

# 🏗 System Architecture

```text
                        ┌─────────────────┐
                        │     Internet    │
                        └────────┬────────┘
                                 │
                                 ▼
                      ┌───────────────────┐
                      │       Nginx       │
                      │ Reverse Proxy     │
                      │ SSL Termination   │
                      └────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Gunicorn Master     │
                    └────────┬─────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
 │ Uvicorn W1   │   │ Uvicorn W2   │   │ Uvicorn W3   │
 └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │      FastAPI      │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │    PostgreSQL     │
                 └───────────────────┘
```

---

# 🛠 Tech Stack

| Layer            | Technology      |
| ---------------- | --------------- |
| Language         | Python 3.10+    |
| API Framework    | FastAPI         |
| ASGI Server      | Uvicorn         |
| Process Manager  | Gunicorn        |
| Database         | PostgreSQL      |
| ORM              | SQLAlchemy      |
| Migrations       | Alembic         |
| Authentication   | JWT             |
| Password Hashing | Bcrypt          |
| Deployment       | AWS EC2 + Nginx |

---

# 📊 Database Design

The application follows a normalized relational database design.

## Core Entities

### Users

Stores:

* Credentials
* Roles
* Authentication information

### Products

Stores:

* Product metadata
* Pricing information

### Inventories

Maintains:

* Available stock
* Warehouse quantities

### Cart Items

Acts as a temporary user-product relationship before checkout.

### Orders

Represents completed purchases.

### Order Items

Captures immutable snapshots of purchased products.

### Reviews

Stores:

* Ratings (1–5)
* Customer feedback

---

# 🔐 Role-Based Access Control

| Role     | Permissions                                                |
| -------- | ---------------------------------------------------------- |
| Admin    | Create products, update inventory                          |
| Customer | Browse products, manage cart, place orders, submit reviews |

Route protection is enforced through dependency injection and role validation middleware.

---

# 🚦 Concurrency Control Strategy

## The Problem

Suppose inventory contains:

```text
Product A
Stock = 1
```

Two customers attempt checkout simultaneously.

Without locking:

```text
Request A reads stock = 1
Request B reads stock = 1

Request A purchases
Request B purchases

Final stock = -1
```

Result:

❌ Overselling

❌ Inventory corruption

---

## The Solution

The checkout engine acquires a PostgreSQL row-level lock:

```python
inventory = (
    db.query(Inventory)
      .filter(
          Inventory.product_id == item.product_id
      )
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

Behavior:

```text
Transaction A acquires lock
Transaction B waits

Transaction A commits
Lock released

Transaction B proceeds
```

Result:

✅ No race conditions

✅ No overselling

✅ Strong consistency guarantees

---

# 📡 API Endpoints

## Authentication

| Method | Endpoint             |
| ------ | -------------------- |
| POST   | `/api/auth/register` |
| POST   | `/api/auth/login`    |

## Products

| Method | Endpoint                       | Access |
| ------ | ------------------------------ | ------ |
| GET    | `/api/products`                | Public |
| POST   | `/api/products`                | Admin  |
| PUT    | `/api/products/{id}/inventory` | Admin  |

## Reviews

| Method | Endpoint                     | Access   |
| ------ | ---------------------------- | -------- |
| POST   | `/api/products/{id}/reviews` | Customer |

## Cart

| Method | Endpoint    | Access   |
| ------ | ----------- | -------- |
| POST   | `/api/cart` | Customer |

## Checkout

| Method | Endpoint        | Access   |
| ------ | --------------- | -------- |
| POST   | `/api/checkout` | Customer |

---

# ⚙️ Local Development Setup

## Clone Repository

```bash
git clone https://github.com/yourusername/ecommerce-backend.git

cd ecommerce-backend
```

## Create Virtual Environment

```bash
python -m venv venv

source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce

SECRET_KEY=your-secret-key
```

## Apply Database Migrations

```bash
alembic upgrade head
```

## Run Server

```bash
uvicorn main:app --reload
```

API Documentation:

```text
http://localhost:8000/docs
```

---

# 📈 Engineering Challenges Solved

### Preventing Overselling

Implemented pessimistic row-level locking with PostgreSQL.

### Maintaining Data Integrity

Wrapped checkout operations inside ACID-compliant transactions.

### Eliminating N+1 Queries

Utilized SQLAlchemy eager loading via `joinedload`.

### Secure Access Control

Implemented JWT authentication and RBAC authorization.

### Scalable Deployment

Designed for horizontal worker scaling behind Gunicorn and Nginx.

---

# 🎯 What This Project Demonstrates

* Backend API Design
* Authentication & Authorization
* Database Modeling
* Transaction Management
* Concurrency Control
* Performance Optimization
* Production Deployment Practices
* PostgreSQL Internals
* Software Architecture

---

## Checkout: `http://13.60.232.161/docs`

## Author

**Prateek Kumar Yadav**

Backend Engineer | Python | FastAPI | PostgreSQL

Built to showcase production-grade backend engineering concepts and real-world scalability patterns.
