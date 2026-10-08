"""
Unit Tests: MCP Server Tools (Read-Only DB Pool, Schema Inspection, Metrics Store)
"""

import pytest
from mcp_server.tools.schema_tools import list_tables, inspect_schema, get_metric_definition
from mcp_server.tools.query_tools import execute_readonly_sql, explain_plan


def test_list_tables():
    tables = list_tables()
    assert "clients" in tables
    assert "instruments" in tables
    assert "orders" in tables
    assert "trades" in tables


def test_inspect_schema_clients():
    schema = inspect_schema("clients")
    assert "clients" in schema
    col_names = [c["name"] for c in schema["clients"]["columns"]]
    assert "client_id" in col_names
    assert "tier" in col_names
    assert "zone" in col_names
    assert schema["clients"]["primary_key"] == ["client_id"]


def test_get_metric_definition():
    metric = get_metric_definition("order_fill_rate")
    assert "metric_id" in metric
    assert metric["metric_id"] == "order_fill_rate"
    assert "status = 'COMPLETE'" in metric["formula"]
    assert "orders" in metric["tables"]


def test_execute_readonly_sql_success():
    res = execute_readonly_sql("SELECT COUNT(*) AS total_clients FROM clients")
    assert res["status"] == "success"
    assert res["row_count"] == 1
    assert res["rows"][0]["total_clients"] == 25000
    assert res["execution_time_ms"] > 0


def test_execute_readonly_sql_error_handling():
    # Intentionally malformed SQL to ensure graceful error return
    res = execute_readonly_sql("SELECT nonexistent_column FROM nonexistent_table")
    assert res["status"] == "error"
    assert res["error"] is not None


def test_explain_plan():
    res = explain_plan("SELECT client_id, tier FROM clients WHERE tier = 'HNI'")
    assert res["status"] == "success"
    assert "plan" in res
