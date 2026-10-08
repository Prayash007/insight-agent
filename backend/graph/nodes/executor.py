"""
InsightAgent LangGraph Node: MCP Query Executor
Dispatches validated read-only SQL queries to the decoupled MCP server.
Routes database errors back to the self-correction loop when errors occur.
"""

import time
import uuid
from backend.graph.state import AgentState, TraceStep
from mcp_server.tools.query_tools import execute_readonly_sql


def executor_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    sqls = state.get("generated_sql", [])
    query_results = []
    error_found = None

    for idx, sql in enumerate(sqls):
        res = execute_readonly_sql(sql)
        query_results.append({
            "query_index": idx,
            "sql": sql,
            **res
        })
        if res.get("status") == "error":
            error_found = res.get("error")
            break

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step_status = "completed" if error_found is None else "failed"
    total_rows = sum(r.get("row_count", 0) for r in query_results if r.get("status") == "success")

    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "executor",
        "title": f"Executed {len(query_results)} Queries via MCP ({total_rows} rows fetched)" if error_found is None else f"MCP Execution Failed: {error_found}",
        "status": step_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "total_rows": total_rows,
            "execution_ms": elapsed_ms,
            "error": error_found
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    if error_found:
        return {
            "query_results": query_results,
            "error_context": f"Database Execution Error: {error_found}",
            "retry_count": state.get("retry_count", 0) + 1,
            "trace": trace
        }

    return {
        "query_results": query_results,
        "error_context": None,
        "trace": trace
    }
