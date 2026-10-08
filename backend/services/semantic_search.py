"""
InsightAgent Semantic Catalog Retriever
Performs hybrid matching over certified business metrics (metrics.yaml) and database schema metadata.
"""

import json
import yaml
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
METRICS_PATH = BASE_DIR / "backend" / "catalog" / "metrics.yaml"
SCHEMA_META_PATH = BASE_DIR / "backend" / "catalog" / "schema_metadata.json"


class SemanticCatalogRetriever:
    """Retrieves business metrics and schema context matching user questions."""

    def __init__(self):
        self.metrics = self._load_metrics()
        self.schema_metadata = self._load_schema_metadata()

    def _load_metrics(self) -> dict[str, Any]:
        if not METRICS_PATH.exists():
            return {}
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("metrics", {})

    def _load_schema_metadata(self) -> dict[str, Any]:
        if not SCHEMA_META_PATH.exists():
            return {}
        with open(SCHEMA_META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def retrieve_relevant_metrics(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Matches user query against metric names, synonyms, and descriptions.
        """
        tokens = set(query.lower().replace("?", "").replace(",", "").split())
        scored_metrics = []

        for metric_id, spec in self.metrics.items():
            score = 0
            name_tokens = set(spec.get("name", "").lower().split())
            synonyms = [s.lower() for s in spec.get("synonyms", [])]
            desc_tokens = set(spec.get("description", "").lower().split())

            # Keyword matching heuristics
            # Exact metric ID match
            if metric_id in query.lower():
                score += 15

            # Synonym match
            for syn in synonyms:
                if syn in query.lower():
                    score += 12

            # Token overlap
            score += len(tokens.intersection(name_tokens)) * 4
            score += len(tokens.intersection(desc_tokens)) * 1

            # Domain-specific heuristics for Angel One
            if any(t in tokens for t in ["f&o", "fno", "derivatives", "options", "futures"]):
                if metric_id in ["gross_turnover", "fno_turnover_share"]:
                    score += 6
            if any(t in tokens for t in ["rejected", "rejection", "margin", "rms"]):
                if metric_id in ["rms_rejection_rate", "total_order_rejection_rate"]:
                    score += 8
            if any(t in tokens for t in ["fill", "success", "execution", "completed"]):
                if metric_id == "order_fill_rate":
                    score += 8
            if any(t in tokens for t in ["yield", "revenue", "commission", "brokerage"]):
                if metric_id in ["net_brokerage", "average_brokerage_yield"]:
                    score += 8
            if any(t in tokens for t in ["client", "user", "trader", "demat"]):
                if metric_id == "active_demat_clients":
                    score += 6

            if score > 0:
                scored_metrics.append({
                    "metric_id": metric_id,
                    "score": score,
                    **spec
                })

        # Sort descending by score
        scored_metrics.sort(key=lambda x: x["score"], reverse=True)
        return scored_metrics[:top_k]

    def retrieve_schema_context(self, matched_metrics: list[dict[str, Any]], query: str) -> dict[str, Any]:
        """
        Assembles table schemas, foreign key relationships, and column aliases required.
        """
        required_tables = set()
        for m in matched_metrics:
            for tbl in m.get("tables", []):
                required_tables.add(tbl)

        # Fallback if no metric matched: include core tables
        if not required_tables:
            required_tables = {"clients", "instruments", "orders", "trades"}
        else:
            # Always ensure joins can be completed (e.g. trades usually joins instruments and clients)
            if "trades" in required_tables:
                required_tables.add("instruments")
                required_tables.add("clients")
            if "orders" in required_tables:
                required_tables.add("instruments")
                required_tables.add("clients")

        tables_data = self.schema_metadata.get("tables", {})
        context_tables = {tbl: tables_data[tbl] for tbl in required_tables if tbl in tables_data}

        # Filter relevant relationships
        all_rels = self.schema_metadata.get("relationships", [])
        context_rels = [
            r for r in all_rels
            if r["source_table"] in required_tables and r["target_table"] in required_tables
        ]

        return {
            "tables": context_tables,
            "relationships": context_rels
        }


retriever = SemanticCatalogRetriever()
