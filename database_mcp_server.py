#!/usr/bin/env python3
"""
Simple Database Analytics MCP Server using FastMCP

This server provides basic database analytics capabilities using SQLite,
showcasing FastMCP's core features: tools, resources, and context.
"""

import csv
from typing import Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from fastmcp import FastMCP, Context

# Global database connection
db_engine: Engine = None
db_session_factory = None
db_path = None


def _is_safe_query(sql: str) -> bool:
    """Check if a SQL query is safe to execute. Only SELECT queries are allowed."""
    sql_lower = sql.lower().strip()
    return sql_lower.startswith("select")


# Initialize FastMCP server
mcp = FastMCP(
    name="DatabaseAnalytics",
    instructions="A simple database analytics server for SQLite databases. "
    "Use tools to connect and query databases, and resources to explore schema and data.",
)

# Tools - Interactive database operations


@mcp.tool
def connect_db(database_path: str) -> Dict[str, Any]:
    """Connect to an SQLite database file."""
    global db_engine, db_session_factory, db_path

    # Close existing connection if any
    if db_engine:
        db_engine.dispose()

    # Create new engine and session factory
    db_engine = create_engine(f"sqlite:///{database_path}")
    db_session_factory = sessionmaker(bind=db_engine)
    db_path = database_path

    return {"success": True, "database_path": database_path}


@mcp.tool
def execute_query(sql: str, ctx: Context = None) -> Dict[str, Any]:
    """Execute a SQL query on the connected database."""
    global db_session_factory

    # Check if query is safe before execution
    if not _is_safe_query(sql):
        return {
            "success": False,
            "error": "Potentially dangerous SQL operations are not allowed. Only SELECT queries are permitted.",
        }

    with db_session_factory() as session:
        # Execute the SQL query
        result = session.execute(text(sql))
        rows = result.fetchall()
        return {"success": True, "results": [dict(row._mapping) for row in rows]}


@mcp.tool
def list_tables() -> Dict[str, Any]:
    """List all tables in the connected database."""
    global db_engine

    # Create database inspector
    inspector = inspect(db_engine)
    # Get all table names
    table_names = inspector.get_table_names()

    return {"success": True, "tables": table_names}


@mcp.tool
def export_to_csv(sql: str, filename: str, ctx: Context = None) -> Dict[str, Any]:
    """Execute a SQL query and export results to CSV file."""
    global db_session_factory

    with db_session_factory() as session:
        # Execute query and get results
        result = session.execute(text(sql))
        rows = result.fetchall()
        columns = list(result.keys())

        # Write results to CSV file
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)

            for row in rows:
                writer.writerow(row)

    return {"success": True, "filename": filename}


# Resources - Read-only data access


@mcp.resource("schema://tables/{table_name}")
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get column information for a specific table."""
    global db_engine

    # Get database inspector
    inspector = inspect(db_engine)

    # Get column information
    columns = inspector.get_columns(table_name)

    # Build column info list
    column_info = []
    for col in columns:
        column_info.append(
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
            }
        )

    return {"table_name": table_name, "columns": column_info}


@mcp.resource("data://tables/{table_name}")
def get_table_data(table_name: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """Get sample rows from a specific table with pagination."""
    global db_session_factory

    with db_session_factory() as session:
        # Get sample data with pagination
        result = session.execute(
            text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset},
        )
        rows = result.fetchall()

        # Convert to dict
        data = [dict(row._mapping) for row in rows]

        return {"table_name": table_name, "sample_data": data}


@mcp.resource("stats://tables/{table_name}")
def get_table_stats(table_name: str) -> Dict[str, Any]:
    """Get comprehensive statistics for a specific table."""
    global db_engine, db_session_factory

    with db_session_factory() as session:
        # Get basic table statistics
        total_rows = session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

    # Get column information
    inspector = inspect(db_engine)
    columns = inspector.get_columns(table_name)

    return {
        "table_name": table_name,
        "total_rows": total_rows,
        "column_count": len(columns),
    }


# Main execution
if __name__ == "__main__":
    print("Starting Database Analytics MCP Server...")
    print("Available tools:")
    print("  - connect_db: Connect to SQLite database")
    print("  - execute_query: Execute SQL queries")
    print("  - list_tables: List all tables")
    print("  - export_to_csv: Export query results to CSV file")
    print("Available resources:")
    print("  - schema://tables/{table_name}: Get table schema")
    print("  - data://tables/{table_name}: Get sample table data")
    print("  - stats://tables/{table_name}: Get basic table statistics")
    print()

    # Run the server
    mcp.run()
