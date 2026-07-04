import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Category, User, UserRole
from app.auth import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

def override_get_db():
    db=TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db]=override_get_db

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()

#prepare data for testing category
@pytest.fixture #fixture prepares and test verifies
def sample_categories(db):
    categories = [
        Category(
            category_name="Electronics",
            category_slug="electronics",
        ),
        Category(
            category_name="Books",
            category_slug="books",
        ),
        Category(
            category_name="Fashion",
            category_slug="fashion",
        )
    ]

    db.add_all(categories)
    db.commit()

    return categories

#Rolechecker and authorization
@pytest.fixture
def admin_user(db):
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

@pytest.fixture
def admin_token(admin_user):
    token = create_access_token(
        data={
            "sub": admin_user.email,
        }
    )

    return token

@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }

#create customer
@pytest.fixture
def customer_user(db):
    user = User(
        email="customer@test.com",
        hashed_password=get_password_hash("customer123"),
        role=UserRole.CUSTOMER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def customer_token(customer_user):
    return create_access_token(
        {"sub": customer_user.email}
    )

@pytest.fixture
def customer_headers(customer_token):
    return {
        "Authorization": f"Bearer {customer_token}"
    }