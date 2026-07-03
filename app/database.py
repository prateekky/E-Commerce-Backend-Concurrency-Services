import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# get PostgreSQL URL from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Removed fallback entirely
    # "postgresql://Inv:password@localhost:5432/ecommerce"
)
if SQLALCHEMY_DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# std synchronous engine for PostgreSQL (using psycopg2 driver)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # appropriate connection pools for high load
    max_overflow=10,  # allow burst connections when pool is full
    pool_pre_ping=True,  # test connections before executing queries to prevent stale sockets
)

# local Session constructor
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative base class for all SQLAlchemy database models
Base = declarative_base()


# initialize our session and perform all our actions
def get_db():
    db = SessionLocal()
    try:
        yield db  # creates db, pauses, and hand it over to route
    finally:
        db.close()  # cleanup guaranteed:ensures connection is returned to the pool even during errors


# def create_table():
#     Base.metadata.create_all(bind=engine)
