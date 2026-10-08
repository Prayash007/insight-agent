"""
InsightAgent MCP Client Service
Interfaces with the decoupled MCP Server to invoke schema and SQL execution tools.
Supports both in-process high-speed execution and remote HTTP/SSE transport.
"""

from typing import Any
import httpx
from backend.config import settings
from mcp_server.tools.schema_tools import (
    list_tables as _in_process_list_tables,
    inspect_schema as _in_process_inspect_schema,
    get_metric_definition as _in_process_get_metric_definition,
)
from mcp_server.tools.query_tools import (
    execute_readonly_sql as _in_process_execute_readonly_sql,
    explain_plan as _in_process_explain_plan,
)


class MCPClient:
    """Unified client to execute MCP tools across in-process or remote SSE servers."""

    def __init__(self, server_url: str = settings.MCP_SERVER_URL, in_process: bool = settings.MCP_USE_IN_PROCESS):
        self.server_url = server_url
        self.in_process = in_process

    async def list_tables(self) -> list[str]:
        if self.in_process:
            return _in_process_list_tables()
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{self.server_url.replace('/sse', '')}/tools/list_tables")
            return resp.json()

    async def inspect_schema(self, table_name: str | None = None) -> dict[str, Any]:
        if self.in_process:
            return _in_process_inspect_schema(table_name)
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{self.server_url.replace('/sse', '')}/tools/inspect_schema", json={"table_name": table_name})
            return resp.json()

    async def get_metric_definition(self, metric_name: str) -> dict[str, Any]:
        if self.in_process:
            return _in_process_get_metric_definition(metric_name)
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{self.server_url.replace('/sse', '')}/tools/get_metric_definition", json={"metric_name": metric_name})
            return resp.json()

    async def execute_readonly_sql(self, sql_query: str, max_rows: int = 500) -> dict[str, Any]:
        if self.in_process:
            return _in_process_execute_readonly_sql(sql_query, max_rows)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.server_url.replace('/sse', '')}/tools/execute_readonly_sql",
                json={"sql_query": sql_query, "max_rows": max_rows}
            )
            return resp.json()

    async def explain_query(self, sql_query: str) -> dict[str, Any]:
        if self.in_process:
            return _in_process_explain_plan(sql_query)
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{self.server_url.replace('/sse', '')}/tools/explain_query", json={"sql_query": sql_query})
            return resp.json()


# Global client instance
mcp_client = MCPClient()
