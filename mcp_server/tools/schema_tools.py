"""
MCP Server Tools: Schema Inspection & Metric Store Access
"""

import yaml
from pathlib import Path
from sqlalchemy import inspect
from mcp_server.db import engine

BASE_DIR = Path(__file__).resolve().parent.parent.parent
METRICS_PATH = BASE_DIR / "backend" / "catalog" / "metrics.yaml"
SCHEMA_META_PATH = BASE_DIR / "backend" / "catalog" / "schema_metadata.json"


def list_tables() -> list[str]:
    """Returns a list of all user tables in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def inspect_schema(table_name: str | None = None) -> dict:
    """
    Returns schema structure (columns, types, nullability, primary & foreign keys).
    If table_name is specified, returns only that table.
    """
    inspector = inspect(engine)
    tables = [table_name] if table_name else inspector.get_table_names()
    schema_info = {}

    for tbl in tables:
        cols = []
        for col in inspector.get_columns(tbl):
            cols.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col.get("default", "")) if col.get("default") is not None else None
            })

        pk = inspector.get_pk_constraint(tbl)
        fks = inspector.get_foreign_keys(tbl)
        indexes = inspector.get_indexes(tbl)

        schema_info[tbl] = {
            "columns": cols,
            "primary_key": pk.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                }
                for fk in fks
            ],
            "indexes": [
                {
                    "name": idx["name"],
                    "column_names": idx["column_names"],
                    "unique": idx.get("unique", False)
                }
                for idx in indexes
            ]
        }
    return schema_info


def get_metric_definition(metric_name: str) -> dict:
    """
    Retrieves certified business metric definition from the YAML semantic catalog.
    """
    if not METRICS_PATH.exists():
        return {"error": f"Metrics catalog not found at {METRICS_PATH}"}

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        catalog = yaml.safe_load(f)

    metrics = catalog.get("metrics", {})
    metric_key = metric_name.strip().lower().replace(" ", "_")

    if metric_key in metrics:
        return {"metric_id": metric_key, **metrics[metric_key]}

    # Check synonyms
    for key, spec in metrics.items():
        synonyms = [s.lower() for s in spec.get("synonyms", [])]
        if metric_key in synonyms or any(s in metric_key for s in synonyms):
            return {"metric_id": key, **spec}

    return {
        "error": f"Metric '{metric_name}' not found in certified catalog.",
        "available_metrics": list(metrics.keys())
    }
