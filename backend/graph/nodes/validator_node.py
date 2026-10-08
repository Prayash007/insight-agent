"""
InsightAgent LangGraph Node: AST Validator Node
Validates AST safety and auto-injects LIMIT clauses across all planned SQL queries.
"""

import time
import uuid
from backend.graph.state import AgentState, TraceStep
from backend.graph.nodes.sql_validator import validate_and_format_sql
from mcp_server.db import engine

TARGET_DIALECT = "postgres" if engine.dialect.name == "postgresql" else "sqlite"


def validator_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    sqls = state.get("generated_sql", [])
    validation_results = []
    sanitized_sqls = []
    error_found = None

    for sql in sqls:
        res = validate_and_format_sql(sql, target_dialect=TARGET_DIALECT)
        validation_results.append(res.model_dump())
        if res.is_valid:
            sanitized_sqls.append(res.validated_sql)
        else:
            error_found = res.error_message
            break

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step_status = "completed" if error_found is None else "failed"

    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "sql_validator",
        "title": "AST Validation: Safe & Compliant" if error_found is None else f"AST Error: {error_found}",
        "status": step_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "is_valid": error_found is None,
            "error": error_found,
            "queries_validated": len(sqls)
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    if error_found:
        return {
            "ast_validation_results": validation_results,
            "error_context": f"AST Validation Error: {error_found}",
            "retry_count": state.get("retry_count", 0) + 1,
            "trace": trace
        }

    return {
        "generated_sql": sanitized_sqls,
        "ast_validation_results": validation_results,
        "error_context": None,
        "trace": trace
    }
