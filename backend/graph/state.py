"""
InsightAgent LangGraph State Definition
Defines the typed agent state passed through the graph workflow and self-correction cycles.
"""

from typing import TypedDict, Literal, Any


class TraceStep(TypedDict):
    step_id: str
    node: str
    title: str
    status: Literal["running", "completed", "failed", "retrying"]
    timestamp: str
    elapsed_ms: float
    details: dict[str, Any]


class SubQueryPlan(TypedDict):
    task_id: str
    description: str
    dimension: str | None
    metric: str
    sql: str | None
    status: Literal["pending", "executed", "failed"]


class AgentState(TypedDict):
    query_id: str
    user_query: str
    session_id: str
    intent: Literal["simple_query", "diagnostic_why", "metric_lookup", "clarification"]
    matched_metrics: list[dict[str, Any]]
    schema_context: dict[str, Any]
    plan: list[SubQueryPlan]
    generated_sql: list[str]
    ast_validation_results: list[dict[str, Any]]
    query_results: list[dict[str, Any]]
    analytics_results: dict[str, Any]
    chart_config: dict[str, Any] | None
    narrative_summary: str
    error_context: str | None
    retry_count: int
    trace: list[TraceStep]
