"""
InsightAgent LangGraph Node: Multi-Query Diagnostic Planner
Decomposes diagnostic 'Why' questions into parallel dimensional cuts, or sets up single-query execution.
"""

import time
import uuid
from backend.graph.state import AgentState, TraceStep, SubQueryPlan


def planner_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    intent = state.get("intent", "simple_query")
    user_query = state.get("user_query", "")
    matched_metrics = state.get("matched_metrics", [])
    primary_metric = matched_metrics[0]["metric_id"] if matched_metrics else "gross_turnover"

    plans: list[SubQueryPlan] = []

    if intent == "diagnostic_why":
        # Root-cause multi-dimensional decomposition
        plans = [
            {
                "task_id": "task_baseline",
                "description": "Compute baseline period vs target period metric totals and calculate net delta.",
                "dimension": "time_period",
                "metric": primary_metric,
                "sql": None,
                "status": "pending"
            },
            {
                "task_id": "task_dim_segment",
                "description": "Segment breakdown: Analyze turnover and trade frequency across instrument types (Index vs Stock).",
                "dimension": "instrument_type",
                "metric": primary_metric,
                "sql": None,
                "status": "pending"
            },
            {
                "task_id": "task_dim_client_tier",
                "description": "Client tier breakdown: Measure variance contribution across Retail, HNI, and Institutional tiers.",
                "dimension": "client_tier",
                "metric": primary_metric,
                "sql": None,
                "status": "pending"
            },
            {
                "task_id": "task_dim_rejection_root_cause",
                "description": "RMS risk checks: Measure order rejection spikes and margin failure percentages.",
                "dimension": "rejection_reason",
                "metric": "rms_rejection_rate",
                "sql": None,
                "status": "pending"
            }
        ]
    elif intent == "metric_lookup":
        plans = []
    else:
        # Standard analytical query plan
        plans = [
            {
                "task_id": "task_primary",
                "description": f"Execute direct analytical aggregation for metric '{primary_metric}'.",
                "dimension": None,
                "metric": primary_metric,
                "sql": None,
                "status": "pending"
            }
        ]

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "planner",
        "title": f"Planned {len(plans)} Dimensional Investigations",
        "status": "completed",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "intent": intent,
            "tasks": [p["description"] for p in plans]
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    return {
        "plan": plans,
        "trace": trace
    }
