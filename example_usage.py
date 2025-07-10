#!/usr/bin/env python3
"""
Example usage of the Database Analytics MCP Server

This script demonstrates how to use the FastMCP client to interact
with the database analytics server.
"""

import asyncio
from pathlib import Path
from sqlalchemy import create_engine, text, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from fastmcp import Client


def create_sample_database():
    """Create a sample SQLite database for testing."""
    db_path = "sample_database.db"

    # Remove existing database
    if Path(db_path).exists():
        Path(db_path).unlink()

    # Create new database with sample data
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Create users table
        session.execute(
            text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )

        # Create orders table
        session.execute(
            text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                price DECIMAL(10,2),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        )

        # Insert sample data
        users_data = [
            (1, "Alice Johnson", "alice@example.com", 28),
            (2, "Bob Smith", "bob@example.com", 35),
            (3, "Charlie Brown", "charlie@example.com", 22),
            (4, "Diana Prince", "diana@example.com", 30),
            (5, "Edward Davis", "edward@example.com", 45),
        ]

        for user_data in users_data:
            session.execute(
                text(
                    "INSERT INTO users (id, name, email, age) VALUES (:id, :name, :email, :age)"
                ),
                {
                    "id": user_data[0],
                    "name": user_data[1],
                    "email": user_data[2],
                    "age": user_data[3],
                },
            )

        orders_data = [
            (1, 1, "Laptop", 1, 999.99),
            (2, 1, "Mouse", 2, 29.99),
            (3, 2, "Keyboard", 1, 79.99),
            (4, 3, "Monitor", 1, 299.99),
            (5, 3, "Webcam", 1, 89.99),
            (6, 4, "Headphones", 1, 149.99),
            (7, 5, "Tablet", 1, 499.99),
            (8, 5, "Charger", 3, 24.99),
        ]

        for order_data in orders_data:
            session.execute(
                text(
                    "INSERT INTO orders (id, user_id, product_name, quantity, price) VALUES (:id, :user_id, :product_name, :quantity, :price)"
                ),
                {
                    "id": order_data[0],
                    "user_id": order_data[1],
                    "product_name": order_data[2],
                    "quantity": order_data[3],
                    "price": order_data[4],
                },
            )

        session.commit()

    print(f"Created sample database: {db_path}")
    return db_path


async def demonstrate_mcp_server(db_path: str, cleanup: bool = True):
    """Demonstrate the MCP server functionality.

    Args:
        db_path: Path to the database file to use
        cleanup: Whether to clean up the database after demo (default: True)
    """

    # Connect to MCP server
    client = Client("./database_mcp_server.py")

    async with client:
        print("=== Database Analytics MCP Server Demo ===\n")

        # 1. Connect to database
        print("1. Connecting to database...")
        result = await client.call_tool("connect_db", {"database_path": db_path})
        print(f"Connection result: {result}")
        print()

        # 2. List tables
        print("2. Listing tables...")
        tables = await client.call_tool("list_tables", {})
        print(f"Tables: {tables}")
        print()

        # 3. Get table schema
        print("3. Getting schema for 'users' table...")
        schema = await client.read_resource("schema://tables/users")
        print(f"Users schema: {schema[0].text}")
        print()

        # 4. Get sample data
        print("4. Getting sample data from 'users' table...")
        data = await client.read_resource("data://tables/users")
        print(f"Users data: {data[0].text}")
        print()

        # 5. Execute a query
        print("5. Executing a query...")
        query_result = await client.call_tool(
            "execute_query",
            {
                "sql": "SELECT u.name, u.email, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name, u.email"
            },
        )
        print(f"Query result: {query_result}")
        print()

        # 6. Get orders schema
        print("6. Getting schema for 'orders' table...")
        orders_schema = await client.read_resource("schema://tables/orders")
        print(f"Orders schema: {orders_schema[0].text}")
        print()

        # 7. Get orders data
        print("7. Getting sample data from 'orders' table...")
        orders_data = await client.read_resource("data://tables/orders")
        print(f"Orders data: {orders_data[0].text}")
        print()

        # 8. Execute aggregation query
        print("8. Executing aggregation query...")
        agg_result = await client.call_tool(
            "execute_query",
            {
                "sql": "SELECT product_name, SUM(quantity) as total_sold, AVG(price) as avg_price FROM orders GROUP BY product_name ORDER BY total_sold DESC"
            },
        )
        print(f"Aggregation result: {agg_result}")
        print()

        print("=== Demo completed successfully! ===")

    # Clean up
    if cleanup and Path(db_path).exists():
        Path(db_path).unlink()
        print(f"Cleaned up database: {db_path}")


if __name__ == "__main__":
    print("Database Analytics MCP Server - Example Usage")
    print("=" * 50)

    async def main():
        # Create sample database
        db_path = create_sample_database()

        # Demonstrate MCP server with the created database
        await demonstrate_mcp_server(db_path, cleanup=False)

    asyncio.run(main())
