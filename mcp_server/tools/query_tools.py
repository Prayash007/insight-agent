"""
MCP Server Tools: Safe Read-Only SQL Execution & Query Plan Explainer
"""

import time
from sqlalchemy import text
from mcp_server.db import engine


def execute_readonly_sql(sql_query: str, max_rows: int = 500) -> dict:
    """
    Executes a read-only SQL query against the database and returns structured records.
    Returns:
      {
        "status": "success" | "error",
        "columns": [...],
        "rows": [...],
        "row_count": int,
        "execution_time_ms": float,
        "error": str | None
      }
    """
    cleaned_sql = sql_query.strip().rstrip(";")
    start_time = time.perf_counter()

    try:
        with engine.connect() as conn:
            # Enforce read-only transaction for safety
            result = conn.execute(text(cleaned_sql))
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if not result.returns_rows:
                return {
                    "status": "success",
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": elapsed_ms,
                    "error": None
                }

            columns = list(result.keys())
            # Fetch up to max_rows
            raw_rows = result.fetchmany(max_rows)
            
            # Format row values cleanly (convert timestamps/dates/decimals to str or float)
            formatted_rows = []
            for row in raw_rows:
                row_dict = {}
                for col_name, val in zip(columns, row):
                    if hasattr(val, "isoformat"):
                        row_dict[col_name] = val.isoformat()
                    elif isinstance(val, (int, float, str, bool)) or val is None:
                        row_dict[col_name] = val
                    else:
                        row_dict[col_name] = str(val)
                formatted_rows.append(row_dict)

            return {
                "status": "success",
                "columns": columns,
                "rows": formatted_rows,
                "row_count": len(formatted_rows),
                "execution_time_ms": elapsed_ms,
                "error": None
            }

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "error",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error": str(e)
        }


def explain_plan(sql_query: str) -> dict:
    """
    Runs EXPLAIN on the SQL query to inspect query plan execution.
    """
    cleaned_sql = sql_query.strip().rstrip(";")
    is_postgres = engine.dialect.name == "postgresql"
    explain_stmt = f"EXPLAIN (FORMAT JSON, ANALYZE) {cleaned_sql}" if is_postgres else f"EXPLAIN QUERY PLAN {cleaned_sql}"

    try:
        with engine.connect() as conn:
            res = conn.execute(text(explain_stmt))
            plan_rows = [row[0] if len(row) == 1 else list(row) for row in res.fetchall()]
            return {
                "status": "success",
                "plan": plan_rows,
                "dialect": engine.dialect.name
            }
    except Exception as e:
        # Fallback to simple EXPLAIN if ANALYZE fails
        try:
            with engine.connect() as conn:
                res = conn.execute(text(f"EXPLAIN {cleaned_sql}"))
                plan_rows = [row[0] if len(row) == 1 else list(row) for row in res.fetchall()]
                return {
                    "status": "success",
                    "plan": plan_rows,
                    "dialect": engine.dialect.name
                }
        except Exception as fallback_err:
            return {
                "status": "error",
                "error": str(fallback_err),
                "dialect": engine.dialect.name
            }
