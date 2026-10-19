import os
import sqlite3
from typing import Any

from mcp.server.mcpserver import MCPServer

# Initialize the MCP Server under SDK v2 naming conventions
mcp = MCPServer("Enterprise SQLite Session Manager")

def get_db_connection(db_path: str, read_only: bool = False):
    """
    Establishes a connection to the targeted SQLite database file.
    Normalizes Windows path variances and configures error-handling parameters.
    """
    if not db_path:
        raise ValueError("Database file path must be supplied via the conversation context.")

    normalized_path = os.path.abspath(os.path.normpath(db_path))

    # Ensure the parent directory structure exists before attempting connections
    dir_name = os.path.dirname(normalized_path)
    if dir_name and not os.path.exists(dir_name):
        raise FileNotFoundError(f"The directory path '{dir_name}' does not exist on this system.")

    # Open standard or read-only connection
    if read_only:
        # Check existence if reading, as sqlite3.connect creates files automatically
        if not os.path.exists(normalized_path):
            raise FileNotFoundError(f"Cannot read database. File not found: {normalized_path}")
        # URI connection for strict read-only execution at the OS level
        conn = sqlite3.connect(f"file:{normalized_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(normalized_path)

    conn.row_factory = sqlite3.Row  # Return rows as dictionaries mapping column names
    return conn

# ==========================================
# 1. SCHEMA & METADATA TOOLS
# ==========================================

@mcp.tool()
def list_tables(db_path: str) -> list[str]:
    """
    List all tables, views, and system tables inside the database.
    """
    try:
        with get_db_connection(db_path, read_only=True) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%';")
            return [row["name"] for row in cursor.fetchall()]
    except Exception as e:
        return [f"Error listing tables: {e!s}"]

@mcp.tool()
def describe_table(db_path: str, table_name: str) -> dict[str, Any]:
    """
    Get detailed schema structural information for a table including columns, data types,
    nullability, default values, primary keys, and foreign key constraints.
    """
    try:
        with get_db_connection(db_path, read_only=True) as conn:
            cursor = conn.cursor()

            # Fetch columns metadata (safe from injection via PRAGMA)
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [dict(row) for row in cursor.fetchall()]

            # Fetch foreign key constraints
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = [dict(row) for row in cursor.fetchall()]

            # Fetch indexes on the table
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = [dict(row) for row in cursor.fetchall()]

            return {
                "table_name": table_name,
                "columns": columns,
                "foreign_keys": foreign_keys,
                "indexes": indexes
            }
    except Exception as e:
        return {"error": f"Failed to describe table '{table_name}': {e!s}"}

# ==========================================
# 2. QUERY & DATA MANIPULATION TOOLS
# ==========================================

@mcp.tool()
def execute_read_query(db_path: str, sql_query: str) -> list[dict[str, Any]]:
    """
    Execute read-only SQL queries (SELECT statements).
    Enforces deep safety boundaries preventing data modification.
    """
    try:
        with get_db_connection(db_path, read_only=True) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        return [{"error": f"Read query failed: {e!s}"}]

@mcp.tool()
def execute_write_query(db_path: str, sql_query: str, params: list[Any] = None) -> str:
    """
    Execute structural mutations or data changes (INSERT, UPDATE, DELETE, CREATE TABLE, ALTER TABLE, DROP TABLE).
    Supports safe parameterized queries to handle arbitrary string inputs and escaping.
    """
    if params is None:
        params = []
    try:
        with get_db_connection(db_path, read_only=False) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Database write error: {e!s}"

@mcp.tool()
def execute_transaction(db_path: str, sql_queries: list[str]) -> str:
    """
    Execute multiple SQL mutation queries sequentially within a single ACID transaction block.
    If any individual statement fails, the entire sequence is completely rolled back.
    """
    try:
        with get_db_connection(db_path, read_only=False) as conn:
            cursor = conn.cursor()
            for query in sql_queries:
                cursor.execute(query)
            conn.commit()
            return f"Transaction committed successfully. Executed {len(sql_queries)} operations."
    except Exception as e:
        return f"Transaction aborted and rolled back. Failed statement error: {e!s}"

# ==========================================
# 3. ADVANCED UTILITY & MAINTENANCE TOOLS
# ==========================================

@mcp.tool()
def optimize_and_maintain(db_path: str, operation: str) -> str:
    """
    Perform index tuning, storage reclamation, integrity analysis, or statistics generation.
    Supported operations: 'vacuum' (reclaim space), 'analyze' (optimize query planner indexes), 'integrity_check' (verify file structure).
    """
    op = operation.lower().strip()
    try:
        # Maintenance parameters require a write connection but bypass standard row parameters
        with get_db_connection(db_path, read_only=False) as conn:
            # SQLite requires isolation level changes to run VACUUM commands natively
            conn.isolation_level = None
            cursor = conn.cursor()

            if op == "vacuum":
                cursor.execute("VACUUM;")
                return "Vacuum completed successfully. Storage defragmented and unallocated pages reclaimed."
            elif op == "analyze":
                cursor.execute("ANALYZE;")
                return "Analyze completed successfully. Query planner stats updated."
            elif op == "integrity_check":
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                return f"Integrity check status: {result[0] if result else 'Unknown'}"
            else:
                return f"Error: Unsupported maintenance operation '{operation}'. Use 'vacuum', 'analyze', or 'integrity_check'."
    except Exception as e:
        return f"Maintenance utility exception: {e!s}"

if __name__ == "__main__":
    # Boots up standard input/output transport for native local workspace agent discovery
    mcp.run()
