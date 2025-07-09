#!/usr/bin/env python3
"""
Simple Database Analytics MCP Server using FastMCP

This server provides basic database analytics capabilities using SQLite,
showcasing FastMCP's core features: tools, resources, and context.
"""

import sqlite3
import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Any
from fastmcp import FastMCP, Context

# Global database connection
db_connection = None
db_path = None

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
    global db_connection, db_path

    try:
        # Convert to Path object and check if file exists
        db_file = Path(database_path)
        if not db_file.exists():
            return {
                "success": False,
                "error": f"Database file not found: {database_path}",
            }

        # Close existing connection if any
        if db_connection:
            db_connection.close()

        # Create new connection
        db_connection = sqlite3.connect(database_path)
        db_connection.row_factory = sqlite3.Row  # Enable dict-like access
        db_path = database_path

        # Test connection with a simple query
        cursor = db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        return {
            "success": True,
            "database_path": database_path,
            "tables_count": len(tables),
            "tables": tables,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to connect to database: {str(e)}"}


@mcp.tool
async def execute_query(sql: str, ctx: Context = None) -> Dict[str, Any]:
    """Execute a SQL query on the connected database."""
    global db_connection

    if not db_connection:
        return {
            "success": False,
            "error": "No database connection. Use connect_db first.",
        }

    try:
        # Log query execution
        if ctx:
            await ctx.info(f"Executing query: {sql[:100]}...")

        # Basic SQL safety check
        sql_lower = sql.lower().strip()
        if any(
            dangerous in sql_lower
            for dangerous in ["drop", "delete", "truncate", "alter"]
        ):
            return {
                "success": False,
                "error": "Potentially dangerous SQL operations are not allowed",
            }

        # Execute query with timing
        start_time = time.time()
        cursor = db_connection.cursor()
        cursor.execute(sql)
        execution_time = time.time() - start_time

        # Get results
        if sql_lower.startswith("select"):
            rows = cursor.fetchall()
            # Convert sqlite3.Row to dict
            results = [dict(row) for row in rows]

            if ctx:
                await ctx.info(
                    f"Query returned {len(results)} rows in {execution_time:.3f}s"
                )

            return {
                "success": True,
                "row_count": len(results),
                "results": results,
                "columns": [description[0] for description in cursor.description],
                "execution_time_seconds": round(execution_time, 3),
            }
        else:
            # For non-SELECT queries
            db_connection.commit()
            return {
                "success": True,
                "rows_affected": cursor.rowcount,
                "message": "Query executed successfully",
                "execution_time_seconds": round(execution_time, 3),
            }

    except sqlite3.Error as e:
        if ctx:
            await ctx.error(f"SQL error: {str(e)}")
        return {"success": False, "error": f"SQL error: {str(e)}"}
    except Exception as e:
        if ctx:
            await ctx.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@mcp.tool
def list_tables() -> Dict[str, Any]:
    """List all tables in the connected database."""
    global db_connection

    if not db_connection:
        return {
            "success": False,
            "error": "No database connection. Use connect_db first.",
        }

    try:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = []
        for row in cursor.fetchall():
            tables.append({"name": row[0], "create_sql": row[1]})

        return {"success": True, "table_count": len(tables), "tables": tables}

    except sqlite3.Error as e:
        return {"success": False, "error": f"Failed to list tables: {str(e)}"}


@mcp.tool
async def export_to_csv(sql: str, filename: str, ctx: Context = None) -> Dict[str, Any]:
    """Execute a SQL query and export results to CSV file."""
    global db_connection

    if not db_connection:
        return {
            "success": False,
            "error": "No database connection. Use connect_db first.",
        }

    try:
        # Log query execution
        if ctx:
            await ctx.info(f"Executing query for CSV export: {sql[:100]}...")

        # Basic SQL safety check
        sql_lower = sql.lower().strip()
        if any(
            dangerous in sql_lower
            for dangerous in ["drop", "delete", "truncate", "alter"]
        ):
            return {
                "success": False,
                "error": "Potentially dangerous SQL operations are not allowed",
            }

        # Execute query
        cursor = db_connection.cursor()
        cursor.execute(sql)

        if not sql_lower.startswith("select"):
            return {
                "success": False,
                "error": "Only SELECT queries can be exported to CSV",
            }

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        # Write to CSV file
        file_path = Path(filename)
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(columns)

            # Write data rows
            for row in rows:
                writer.writerow(row)

        if ctx:
            await ctx.info(f"Exported {len(rows)} rows to {filename}")

        return {
            "success": True,
            "filename": str(file_path.absolute()),
            "row_count": len(rows),
            "column_count": len(columns),
            "columns": columns,
        }

    except sqlite3.Error as e:
        if ctx:
            await ctx.error(f"SQL error: {str(e)}")
        return {"success": False, "error": f"SQL error: {str(e)}"}
    except Exception as e:
        if ctx:
            await ctx.error(f"Export error: {str(e)}")
        return {"success": False, "error": f"Export error: {str(e)}"}


# Resources - Read-only data access


@mcp.resource("schema://tables/{table_name}")
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get column information for a specific table."""
    global db_connection

    if not db_connection:
        return {"error": "No database connection. Use connect_db tool first."}

    try:
        cursor = db_connection.cursor()

        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            return {"error": f"Table '{table_name}' not found"}

        column_info = []
        for col in columns:
            column_info.append(
                {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default_value": col[4],
                    "primary_key": bool(col[5]),
                }
            )

        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()

        fk_info = []
        for fk in foreign_keys:
            fk_info.append(
                {"column": fk[3], "references_table": fk[2], "references_column": fk[4]}
            )

        return {
            "table_name": table_name,
            "columns": column_info,
            "foreign_keys": fk_info,
            "column_count": len(column_info),
        }

    except sqlite3.Error as e:
        return {"error": f"Failed to get schema for table '{table_name}': {str(e)}"}


@mcp.resource("data://tables/{table_name}")
def get_table_data(table_name: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """Get sample rows from a specific table with pagination."""
    global db_connection

    if not db_connection:
        return {"error": "No database connection. Use connect_db tool first."}

    try:
        cursor = db_connection.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )

        if not cursor.fetchone():
            return {"error": f"Table '{table_name}' not found"}

        # Get sample data with pagination
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]

        # Convert to dict
        data = [dict(row) for row in rows]

        # Calculate pagination info
        has_more = (offset + len(data)) < total_rows
        next_offset = offset + len(data) if has_more else None

        # Calculate basic statistics for each column
        statistics = {}
        if data:
            column_names = list(data[0].keys())
            for col in column_names:
                values = [row[col] for row in data if row[col] is not None]
                null_count = sum(1 for row in data if row[col] is None)

                stats = {
                    "null_count": null_count,
                    "non_null_count": len(data) - null_count,
                    "unique_count": len(set(values)) if values else 0,
                }

                # Add type-specific statistics
                if values:
                    if isinstance(values[0], (int, float)):
                        stats.update(
                            {
                                "min": min(values),
                                "max": max(values),
                                "avg": sum(values) / len(values) if values else None,
                            }
                        )
                    elif isinstance(values[0], str):
                        stats.update(
                            {
                                "min_length": min(len(str(v)) for v in values),
                                "max_length": max(len(str(v)) for v in values),
                                "avg_length": sum(len(str(v)) for v in values)
                                / len(values),
                            }
                        )

                statistics[col] = stats

        return {
            "table_name": table_name,
            "sample_data": data,
            "sample_size": len(data),
            "total_rows": total_rows,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
            "next_offset": next_offset,
            "statistics": statistics,
        }

    except sqlite3.Error as e:
        return {"error": f"Failed to get data from table '{table_name}': {str(e)}"}


@mcp.resource("stats://tables/{table_name}")
def get_table_stats(table_name: str) -> Dict[str, Any]:
    """Get comprehensive statistics for a specific table."""
    global db_connection

    if not db_connection:
        return {"error": "No database connection. Use connect_db tool first."}

    try:
        cursor = db_connection.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )

        if not cursor.fetchone():
            return {"error": f"Table '{table_name}' not found"}

        # Get basic table statistics
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]

        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_count = len(columns)

        # Get table size (approximate for SQLite)
        cursor.execute(
            """
            SELECT page_count * page_size as size 
            FROM pragma_page_count(?), pragma_page_size
        """,
            (table_name,),
        )
        table_size = cursor.fetchone()[0] if cursor.fetchone() else 0

        # Get index information
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        index_count = len(indexes)

        # Calculate column statistics for each column
        column_stats = {}
        for col in columns:
            col_name = col[1]
            col_type = col[2]

            # Get null count
            cursor.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL"
            )
            null_count = cursor.fetchone()[0]

            # Get unique count (with limit for performance)
            cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
            unique_count = cursor.fetchone()[0]

            stats = {
                "type": col_type,
                "null_count": null_count,
                "non_null_count": total_rows - null_count,
                "unique_count": unique_count,
                "null_percentage": (null_count / total_rows * 100)
                if total_rows > 0
                else 0,
            }

            column_stats[col_name] = stats

        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "column_count": column_count,
            "table_size_bytes": table_size,
            "index_count": index_count,
            "column_statistics": column_stats,
        }

    except sqlite3.Error as e:
        return {"error": f"Failed to get statistics for table '{table_name}': {str(e)}"}


# Main execution
if __name__ == "__main__":
    print("Starting Database Analytics MCP Server...")
    print("Available tools:")
    print("  - connect_db: Connect to SQLite database")
    print("  - execute_query: Execute SQL queries with timing")
    print("  - list_tables: List all tables")
    print("  - export_to_csv: Export query results to CSV file")
    print("Available resources:")
    print("  - schema://tables/{table_name}: Get table schema")
    print(
        "  - data://tables/{table_name}: Get sample table data with pagination and statistics"
    )
    print("  - stats://tables/{table_name}: Get comprehensive table statistics")
    print()

    # Run the server
    mcp.run()
