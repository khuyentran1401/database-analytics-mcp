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

1. **Install UV (recommended):**

   ```bash
   # Install UV if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**

   ```bash
   # UV automatically manages dependencies from pyproject.toml
   uv sync
   ```

3. **Test the server:**

   ```bash
   uv run example_usage.py
   ```

4. **Add to Claude Code (optional):**

   ```bash
   # Quick setup
   claude mcp add database-analytics -- uv run database_mcp_server.py
   ```

   **Verify installation:**
   ```bash
   # Check if the server is registered
   claude mcp list
   ```

## Using with Claude Code

### Quick Setup (Recommended)

The easiest way to add the server to Claude Code is using the command line:

```bash
# Navigate to the project directory
cd /path/to/fastmcp_examples

# Add the server to Claude Code
claude mcp add database-analytics -- uv run database_mcp_server.py
```

### Manual Configuration (Alternative)

You can also manually add the server to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "database-analytics": {
      "command": "uv",
      "args": ["run", "database_mcp_server.py"],
      "cwd": "/path/to/fastmcp_examples"
    }
  }
}
```

### Usage with Claude Code

Once configured, you can use the server directly in Claude Code:

```text
Connect to my SQLite database at ./data/sales.db
```

Claude will automatically discover and use the `connect_db` tool.

```text
Show me the schema for the users table
```

Claude will use the `schema://tables/users` resource to get table structure.

```text
Execute this query: SELECT product_name, SUM(quantity) FROM orders GROUP BY product_name
```

Claude will use the `execute_query` tool with proper safety checks.

### Troubleshooting Claude Code Setup

**If `claude mcp add` doesn't work:**
- Ensure you have Claude Code CLI installed
- Check that you're in the correct project directory
- Verify the server file exists: `ls database_mcp_server.py`

**If the server doesn't start:**
- Test the server manually: `uv run database_mcp_server.py`
- Check the Claude Code logs for error messages
- Ensure UV is installed and accessible in your PATH

## Using with Other MCP Clients

### Generic MCP Client Configuration

For any MCP client that supports the standard protocol:

```yaml
servers:
  - name: database-analytics
    transport:
      type: stdio
      command: uv
      args: ["run", "database_mcp_server.py"]
```

### Direct FastMCP Client Usage

```python
from fastmcp import Client

async def use_database_server():
    client = Client("./database_mcp_server.py")
    
    async with client:
        # Connect to database
        result = await client.call_tool("connect_db", {
            "database_path": "my_database.db"
        })
        
        # Execute query
        query_result = await client.call_tool("execute_query", {
            "sql": "SELECT * FROM users LIMIT 5"
        })
        
        # Get table schema
        schema = await client.read_resource("schema://tables/users")
        
        # Get sample data
        data = await client.read_resource("data://tables/users")
```

## Example Workflows

### Data Exploration with Claude Code

1. **Connect to Database**

   ```text
   Connect to my SQLite database at ./analytics.db
   ```

2. **Explore Schema**

   ```text
   What tables are available in this database?
   ```

3. **Examine Table Structure**

   ```text
   Show me the schema for the sales table
   ```

4. **Preview Data**

   ```text
   Show me some sample data from the customers table
   ```

5. **Run Analytics Queries**

   ```text
   Calculate total sales by product category
   ```

6. **Export Results**

   ```text
   Export my query results to CSV file called sales_report.csv
   ```

7. **Get Table Statistics**

   ```text
   Show me detailed statistics for the customers table
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

## Troubleshooting

### Common Issues

1. **"No database connection" error**
   - Use `connect_db` tool first before running queries

2. **"Potentially dangerous SQL operations are not allowed"**
   - The server blocks DROP, DELETE, TRUNCATE, ALTER for safety
   - Use for read-only analysis only

3. **"Table not found" error**
   - Use `list_tables` to see available tables
   - Check table name spelling

### Configuration Tips

- **Full paths**: Use absolute paths for database files in production
- **Permissions**: Ensure the server has read access to database files
- **SQLite version**: Works with any SQLite database (version 3.x)
- **UV advantages**: UV provides dependency isolation, faster execution, and better project management

## File Structure

```text
fastmcp_examples/
├── database_mcp_server.py    # Main MCP server implementation
├── example_usage.py          # Usage examples with sample data
├── pyproject.toml           # UV project configuration
├── requirements.txt          # Dependencies (legacy)
├── implementation_plan.md    # Detailed project plan
└── README.md                # This file
```

## Technical Details

### FastMCP Features Demonstrated

1. **@mcp.tool decorator**: Converting Python functions to MCP tools
2. **@mcp.resource decorator**: Dynamic resource templates with URI parameters
3. **Context object**: Progress reporting and logging integration
4. **Structured output**: Automatic JSON serialization
5. **Error handling**: User-friendly error responses

### Safety Implementation

- **SQL Injection Prevention**: Validates queries against dangerous operations
- **Read-only Operations**: Resources provide safe data access
- **Error Handling**: Comprehensive error messages for debugging
- **Connection Management**: Proper SQLite connection lifecycle

## Extending the Server

This implementation can be extended with:

- **Multiple database support** (PostgreSQL, MySQL)
- **Advanced query features** (parameters, prepared statements)
- **Data visualization** (charts, graphs)
- **Export capabilities** (CSV, Excel)
- **AI integration** (natural language to SQL)

See `implementation_plan.md` for detailed extension roadmap.

## License

MIT License - Feel free to use and modify for your projects.

## Why UV?

UV provides several advantages over traditional Python execution:

- **Dependency Isolation**: Each project has its own isolated environment
- **Faster Execution**: UV is written in Rust and starts faster than Python
- **Better Project Management**: Handles dependencies, scripts, and environments
- **Modern Python Tooling**: Follows current best practices for Python development
- **Zero Configuration**: Works out of the box with pyproject.toml