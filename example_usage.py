#!/usr/bin/env python3
"""
Example usage of the Database Analytics MCP Server

This script demonstrates how to use the FastMCP client to interact
with the database analytics server.
"""

import asyncio
from pathlib import Path
from fastmcp import Client
from setup_database import create_sample_database


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
        # Check if database exists, create if it doesn't
        db_path = "ecommerce.db"
        if not Path(db_path).exists():
            print(f"Database {db_path} not found. Creating it...")
            create_sample_database(db_path)
        else:
            print(f"Using existing database: {db_path}")

        # Demonstrate MCP server with the database
        await demonstrate_mcp_server(db_path, cleanup=False)

    asyncio.run(main())
