"""
InsightAgent LangGraph Node: Intent Router
Classifies incoming natural language user questions into workflow intents:
  - diagnostic_why: Root-cause investigations requiring multi-dimensional decomposition.
  - metric_lookup: Direct inquiries about certified formulas in metrics.yaml.
  - simple_query: Standard aggregations, filters, time-series, or top-N queries.
  - clarification: Underspecified questions.
"""

import time
import uuid
from backend.graph.state import AgentState, TraceStep


def router_node(state: AgentState) -> dict:
    """Classifies query intent and initializes trace step."""
    start_time = time.perf_counter()
    user_query = state.get("user_query", "").strip()
    query_lower = user_query.lower()

    # Rule-based intent classification
    why_keywords = ["why", "what caused", "reason for", "explain the drop", "explain the surge", "investigate", "driver of", "root cause"]
    metric_lookup_keywords = ["formula for", "how is", "definition of", "how do we calculate", "what does the metric", "explain metric"]

    if any(k in query_lower for k in metric_lookup_keywords):
        intent = "metric_lookup"
    elif any(k in query_lower for k in why_keywords):
        intent = "diagnostic_why"
    elif len(query_lower) < 4:
        intent = "clarification"
    else:
        intent = "simple_query"

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "router",
        "title": f"Intent Classified: {intent.upper()}",
        "status": "completed",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "intent": intent,
            "query": user_query
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    return {
        "intent": intent,
        "trace": trace
    }
