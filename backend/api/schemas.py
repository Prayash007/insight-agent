"""
InsightAgent API Request/Response Schemas & SSE Event Contracts
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language analytical question from user")
    session_id: str = Field(default="default_session", description="Conversational session ID")


class KPICard(BaseModel):
    label: str
    value: str
    delta: str = ""
    status: Literal["positive", "negative", "neutral"] = "neutral"


class ChartConfig(BaseModel):
    chart_type: Literal["line", "bar", "stacked_bar", "area", "kpi_grid"]
    title: str
    x_key: str | None = None
    y_keys: list[str] = []
    series_labels: dict[str, str] = {}
    kpi_cards: list[dict[str, Any]] = []
    data: list[dict[str, Any]] = []


class TraceStepEvent(BaseModel):
    step_id: str
    node: str
    title: str
    status: Literal["running", "completed", "failed", "retrying"]
    timestamp: str
    elapsed_ms: float
    details: dict[str, Any] = {}


class QueryResponse(BaseModel):
    query_id: str
    user_query: str
    intent: str
    narrative_summary: str
    chart_config: dict[str, Any] | None = None
    generated_sql: list[str] = []
    trace: list[dict[str, Any]] = []
    analytics_summary: dict[str, Any] = {}
