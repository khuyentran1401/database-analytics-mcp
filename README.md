# Database Analytics MCP Server

A practical database analytics MCP server built with FastMCP, providing SQLite database operations through the Model Context Protocol (MCP). Perfect for data analysis workflows with AI assistants like Claude.

## What This Server Provides

### 🛠️ **Tools** (Interactive Operations)

- **`connect_db`** - Connect to SQLite database files
- **`execute_query`** - Execute SQL queries with safety checks
- **`list_tables`** - List all tables in the database

### 📊 **Resources** (Read-only Data Access)

- **`schema://tables/{table_name}`** - Get table column information and structure
- **`data://tables/{table_name}`** - Get sample table data for preview

### 🔐 **Safety Features**

- SQL injection prevention with dangerous operation blocking
- Read-only resource access for safe schema exploration
- Comprehensive error handling with descriptive messages

## Setup and Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/khuyentran1401/database-analytics-mcp.git
   cd database-analytics-mcp
   ```

2. **Install UV (recommended):**

   ```bash
   # Install UV if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies:**

   ```bash
   # UV automatically manages dependencies from pyproject.toml
   uv sync
   ```

4. **Test the server:**

   ```bash
   uv run example_usage.py
   ```

5. **Add to Claude Code**

   ```bash
   # Quick setup
   claude mcp add database-analytics -- uv run database_mcp_server.py
   ```

   **Verify installation:**
   ```bash
   # Check if the server is registered
   claude mcp list
   ```

## Other MCP Clients

For any MCP client that supports the standard protocol:

```yaml
servers:
  - name: database-analytics
    transport:
      type: stdio
      command: uv
      args: ["run", "database_mcp_server.py"]
```

## Example Workflows

### Data Exploration with Claude Code

1. **Connect to Database**

   ```text
   Connect to my SQLite database at ./sample_database.db
   ```

2. **Explore Schema**

   ```text
   What tables are available in this database?
   ```

3. **Examine Table Structure**

   ```text
   Show me the schema for the users table
   ```

4. **Preview Data**

   ```text
   Show me some sample data from the users table
   ```

5. **Run Analytics Queries**

   ```text
   Calculate total sales by product category
   ```

6. **Export Results**

   ```text
   Export the query "SELECT product_name, SUM(quantity) as total_sold FROM orders GROUP BY product_name" to CSV file called sales_report.csv
   ```

7. **Get Table Statistics**

   ```text
   Show me statistics for the users table
   ```

### Common Use Cases

- **Database Schema Discovery**: Quickly understand database structure
- **Data Quality Checks**: Sample data to verify data integrity
- **Ad-hoc Analysis**: Run custom SQL queries safely
- **Report Generation**: Execute complex analytical queries
- **Data Exploration**: Browse tables and relationships with pagination
- **Data Export**: Export query results to CSV for external analysis
- **Performance Monitoring**: Track query execution times

## Available Tools & Resources

### Tools (Interactive Operations)

| Tool | Parameters | Description |
|------|------------|-------------|
| `connect_db` | `database_path: str` | Connect to SQLite database file |
| `execute_query` | `sql: str` | Execute SQL query with safety checks and timing |
| `list_tables` | None | List all tables in connected database |
| `export_to_csv` | `sql: str`, `filename: str` | Export query results to CSV file |

### Resources (Read-only Access)

| Resource URI | Description |
|-------------|-------------|
| `schema://tables/{table_name}` | Get column info, types, constraints, foreign keys |
| `data://tables/{table_name}` | Get sample rows with pagination, statistics (limit, offset) |
| `stats://tables/{table_name}` | Get comprehensive table statistics and column analysis |

