import enum
from sqlalchemy import Column, Integer, String, Float,Numeric, ForeignKey, DateTime, Enum, text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

#define roles
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

#schema for user and establishing relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reviews=relationship("Review", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

#products schema and their relation with inventory
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Numeric(10,2), nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reviews=relationship("Review", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    category=relationship("Category", back_populates="products")

#inventory schema
class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product", back_populates="inventory")

#cart item schema with its connection with product using foreign key
class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

#order schema with connection with user table using foreign key
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

#order_item schema with connection with orders table table using foreign
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10,2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

#reviews table schema
class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id"),
    )

    id= Column(Integer, primary_key=True, index=True)
    product_id=Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id=Column(Integer, ForeignKey("users.id"), nullable=False)
    rating=Column(Integer, nullable=False)#validation in pydantic! i.e., schema
    comment=Column(String)
    created_at=Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #relationships back to parent tables!
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Category(Base):
    __tablename__="categories"

    id=Column(Integer, primary_key=True, index=True)
    category_name=Column(String(50), nullable=False, index=True)
    category_slug=Column(String(50),nullable=False,unique=True,index=True)
    created_at=Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #relationship back to product
    products=relationship("Product", back_populates="category")