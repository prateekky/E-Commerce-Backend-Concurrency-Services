from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
# from app.database import engine, Base

# Standard FastAPI Import Style:
from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.checkout import router as checkout_router
from app.routers.cart import router as cart_router
from app.routers.category import router as category_router

app = FastAPI(
    title="E-Commerce Backend & Concurrency Services",
    description="Engineered using FastAPI, PostgreSQL, SQLAlchemy, and row-level pessimistic locking.",
    version="1.0.0",
)

# Base.metadata.create_all(bind=engine)

# CORS for web integrations (replace * with secure origins in production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# standard API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(category_router, prefix="/api")


@app.get("/", tags=["Root"])
def root_status():
    return {
        "service": "E-Commerce Backend API Engine",
        "engine": "FastAPI with ASGI Uvicorn",
        "database": "PostgreSQL via SQLAlchemy Transactions",
        "health": "healthy",
    }
