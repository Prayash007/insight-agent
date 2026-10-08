"""
Unit Tests: AST SQL Validator & Security Guardrails
"""

import pytest
from backend.graph.nodes.sql_validator import validate_and_format_sql


def test_valid_select_injects_limit():
    sql = "SELECT client_id, name, tier FROM clients WHERE tier = 'HNI'"
    res = validate_and_format_sql(sql)
    assert res.is_valid is True
    assert "LIMIT 500" in res.validated_sql
    assert res.ast_summary["limit"] == 500
    assert "clients" in res.ast_summary["tables"]


def test_select_preserves_smaller_limit():
    sql = "SELECT * FROM trades LIMIT 25"
    res = validate_and_format_sql(sql)
    assert res.is_valid is True
    assert "LIMIT 25" in res.validated_sql
    assert res.ast_summary["limit"] == 25


def test_select_clamps_excessive_limit():
    sql = "SELECT * FROM orders LIMIT 5000"
    res = validate_and_format_sql(sql)
    assert res.is_valid is True
    assert "LIMIT 500" in res.validated_sql
    assert res.ast_summary["limit"] == 500


def test_reject_drop_table():
    sql = "DROP TABLE clients"
    res = validate_and_format_sql(sql)
    assert res.is_valid is False
    assert "Disallowed" in res.error_message


def test_reject_update_statement():
    sql = "UPDATE clients SET tier = 'SUPER_HNI' WHERE client_id = 'CL_00001'"
    res = validate_and_format_sql(sql)
    assert res.is_valid is False
    assert "Disallowed" in res.error_message


def test_reject_system_catalog_access():
    sql = "SELECT * FROM pg_catalog.pg_tables"
    res = validate_and_format_sql(sql)
    assert res.is_valid is False
    assert "Security Violation" in res.error_message


def test_reject_information_schema():
    sql = "SELECT table_name FROM information_schema.tables"
    res = validate_and_format_sql(sql)
    assert res.is_valid is False
    assert "Security Violation" in res.error_message


def test_valid_join_and_group_by():
    sql = """
    SELECT 
        i.segment, 
        COUNT(t.trade_id) AS trade_count,
        SUM(t.turnover) AS total_turnover
    FROM trades t
    JOIN instruments i ON t.instrument_id = i.instrument_id
    GROUP BY i.segment
    """
    res = validate_and_format_sql(sql)
    assert res.is_valid is True
    assert res.ast_summary["has_joins"] is True
    assert res.ast_summary["has_group_by"] is True
    assert res.ast_summary["has_aggregations"] is True
