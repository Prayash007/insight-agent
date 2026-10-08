"""
InsightAgent AST Query Validator & Safety Guardrails
Leverages sqlglot AST parsing to enforce strict enterprise query safety:
  1. Enforces root AST node is strictly a SELECT or UNION expression (no DDL/DML mutations).
  2. Rejects system catalog access (pg_catalog, information_schema, sqlite_master).
  3. Disallows malicious functions (e.g., pg_sleep, dblink).
  4. Enforces/injects LIMIT 500 if omitted or excessive.
  5. Transpiles cleanly to target SQL dialect (PostgreSQL or SQLite).
"""

from typing import Any
import sqlglot
from sqlglot import exp
from pydantic import BaseModel

SYSTEM_CATALOGS = {
    "pg_catalog", "information_schema", "sqlite_master", "sqlite_temp_master",
    "pg_stat_activity", "pg_tables", "pg_database", "pg_user", "performance_schema", "sys"
}

DISALLOWED_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Grant,
    exp.Revoke,
    exp.Command,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
)

DANGEROUS_FUNCTIONS = {
    "pg_sleep", "pg_read_file", "pg_write_file", "dblink", "query_to_xml",
    "load_extension", "system", "exec", "eval"
}


class ASTValidationResult(BaseModel):
    is_valid: bool
    validated_sql: str | None = None
    error_message: str | None = None
    ast_summary: dict[str, Any] = {}


def validate_and_format_sql(raw_sql: str, target_dialect: str = "postgres") -> ASTValidationResult:
    """
    Parses and verifies SQL string via AST analysis.
    If valid, returns sanitized, dialect-formatted SQL with injected LIMIT 500.
    """
    cleaned_sql = raw_sql.strip().rstrip(";")
    if not cleaned_sql:
        return ASTValidationResult(
            is_valid=False,
            error_message="Empty SQL query provided."
        )

    # 1. Parse AST
    try:
        # Tolerant read with fallback
        try:
            parsed = sqlglot.parse_one(cleaned_sql, read="postgres")
        except Exception:
            parsed = sqlglot.parse_one(cleaned_sql)
    except Exception as e:
        return ASTValidationResult(
            is_valid=False,
            error_message=f"SQL Syntax Parsing Error: {str(e)}"
        )

    # 2. Enforce Root Expression is SELECT or UNION
    if isinstance(parsed, DISALLOWED_EXPRESSIONS):
        return ASTValidationResult(
            is_valid=False,
            error_message=f"Disallowed root statement type: '{type(parsed).__name__}'. Only read-only SELECT queries are permitted."
        )

    if not isinstance(parsed, (exp.Select, exp.Union)):
        return ASTValidationResult(
            is_valid=False,
            error_message=f"Invalid root statement: '{type(parsed).__name__}'. Query must be a SELECT expression."
        )

    # 3. Check for any nested DML or DDL inside subqueries or CTEs
    for node in parsed.walk():
        if isinstance(node, DISALLOWED_EXPRESSIONS):
            return ASTValidationResult(
                is_valid=False,
                error_message=f"Disallowed nested statement: '{type(node).__name__}'."
            )

    # 4. Check Tables for System Catalogs
    tables_found = []
    for table_node in parsed.find_all(exp.Table):
        tbl_name = (table_node.name or "").lower()
        db_name = (table_node.db or "").lower()
        tables_found.append(f"{db_name}.{tbl_name}" if db_name else tbl_name)

        if db_name in SYSTEM_CATALOGS or tbl_name in SYSTEM_CATALOGS or tbl_name.startswith("pg_"):
            return ASTValidationResult(
                is_valid=False,
                error_message=f"Security Violation: Access to system catalog '{db_name or tbl_name}' is strictly rejected."
            )

    # 5. Check for Dangerous Functions
    for func in parsed.find_all(exp.Anonymous):
        func_name = (func.name or "").lower()
        if func_name in DANGEROUS_FUNCTIONS:
            return ASTValidationResult(
                is_valid=False,
                error_message=f"Security Violation: Function '{func_name}' is blocked."
            )

    # 6. Automatic LIMIT 500 Enforcement
    # Inspect top-level LIMIT clause
    limit_node = parsed.args.get("limit")
    if limit_node is None:
        parsed = parsed.limit(500)
        limit_applied = 500
    else:
        # Check current limit value
        try:
            current_limit = int(limit_node.expression.this)
            if current_limit > 500:
                limit_node.set("expression", exp.Literal.number(500))
                limit_applied = 500
            else:
                limit_applied = current_limit
        except Exception:
            parsed = parsed.limit(500)
            limit_applied = 500

    # 7. Transpile to target dialect
    formatted_sql = parsed.sql(dialect=target_dialect, pretty=True)

    ast_summary = {
        "root_type": type(parsed).__name__,
        "tables": list(set(tables_found)),
        "limit": limit_applied,
        "has_joins": len(list(parsed.find_all(exp.Join))) > 0,
        "has_aggregations": len(list(parsed.find_all(exp.AggFunc))) > 0,
        "has_group_by": parsed.args.get("group") is not None,
    }

    return ASTValidationResult(
        is_valid=True,
        validated_sql=formatted_sql,
        ast_summary=ast_summary
    )
