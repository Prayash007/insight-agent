"""
InsightAgent MCP Server
Decoupled Model Context Protocol (MCP) Server exposing capital markets data tools over Server-Sent Events (SSE).
"""

import os
import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp_server.tools.schema_tools import list_tables as _list_tables, inspect_schema as _inspect_schema, get_metric_definition as _get_metric_definition
from mcp_server.tools.query_tools import execute_readonly_sql as _execute_readonly_sql, explain_plan as _explain_plan

# Initialize MCP Server instance
mcp = MCPServer(
    name="insight-agent-capital-markets-mcp",
    version="1.0.0",
    description="Decoupled MCP Server providing read-only capital markets data and semantic metric catalog tools for Angel One domain."
)


@mcp.tool()
def list_tables() -> list[str]:
    """
    List all available tables in the capital markets database (clients, instruments, orders, trades).
    """
    return _list_tables()


@mcp.tool()
def inspect_schema(table_name: str | None = None) -> dict:
    """
    Inspect the schema of tables, returning column names, data types, nullability, primary keys, and foreign keys.
    """
    return _inspect_schema(table_name)


@mcp.tool()
def get_metric_definition(metric_name: str) -> dict:
    """
    Fetch certified metric definitions, formulas, and dimension breakdowns from the semantic metric store (metrics.yaml).
    """
    return _get_metric_definition(metric_name)


@mcp.tool()
def execute_readonly_sql(sql_query: str, max_rows: int = 500) -> dict:
    """
    Safely execute a read-only SELECT query against the capital markets database.
    Enforces statement timeouts (2500ms) and returns structured columns, rows, execution time, and error messages.
    """
    return _execute_readonly_sql(sql_query, max_rows)


@mcp.tool()
def explain_query(sql_query: str) -> dict:
    """
    Explain the execution plan for a SQL query to verify index usage and query efficiency.
    """
    return _explain_plan(sql_query)


# Create SSE Starlette ASGI application
sse_app = mcp.sse_app()


def start_server(host: str = "0.0.0.0", port: int = 8001):
    """Run MCP server over SSE using Uvicorn."""
    print(f"Starting InsightAgent MCP Server (SSE) on http://{host}:{port}/sse ...")
    uvicorn.run(sse_app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    start_server(host=host, port=port)
