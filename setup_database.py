#!/usr/bin/env python3
"""
Database setup for FastMCP examples.

Creates a sample e-commerce database with users and orders tables.
"""

from pathlib import Path
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to orders
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2))
    order_date = Column(DateTime, default=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="orders")


def create_sample_database(db_path: str = "ecommerce.db"):
    """Create a comprehensive e-commerce database using SQLAlchemy models"""

    # Remove existing database for clean start
    if Path(db_path).exists():
        Path(db_path).unlink()

    # Create new database with SQLAlchemy
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)  # Creates all tables

    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Create users using model instances
        users = [
            User(id=1, name="Alice Johnson", email="alice@example.com", age=28),
            User(id=2, name="Bob Smith", email="bob@example.com", age=35),
            User(id=3, name="Charlie Brown", email="charlie@example.com", age=22),
            User(id=4, name="Diana Prince", email="diana@example.com", age=30),
            User(id=5, name="Edward Davis", email="edward@example.com", age=45),
        ]
        session.add_all(users)

        # Create orders using model instances
        orders = [
            Order(id=1, user_id=1, product_name="Laptop", quantity=1, price=999.99),
            Order(id=2, user_id=1, product_name="Mouse", quantity=2, price=29.99),
            Order(id=3, user_id=2, product_name="Keyboard", quantity=1, price=79.99),
            Order(id=4, user_id=3, product_name="Monitor", quantity=1, price=299.99),
            Order(id=5, user_id=3, product_name="Webcam", quantity=1, price=89.99),
            Order(id=6, user_id=4, product_name="Headphones", quantity=1, price=149.99),
            Order(id=7, user_id=5, product_name="Tablet", quantity=1, price=499.99),
            Order(id=8, user_id=5, product_name="Charger", quantity=3, price=24.99),
        ]
        session.add_all(orders)
        session.commit()

    print(f"✅ Created comprehensive e-commerce database: {db_path}")
    return db_path


if __name__ == "__main__":
    # Create database when run directly
    create_sample_database()