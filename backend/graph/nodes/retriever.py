"""
InsightAgent LangGraph Node: Semantic Catalog Retriever
Retrieves certified business formulas and schema context to eliminate mathematical hallucination.
"""

import time
import uuid
from backend.graph.state import AgentState, TraceStep
from backend.services.semantic_search import retriever


def retriever_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    user_query = state.get("user_query", "")

    # Retrieve matching metrics
    matched_metrics = retriever.retrieve_relevant_metrics(user_query, top_k=3)
    schema_context = retriever.retrieve_schema_context(matched_metrics, user_query)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "retriever",
        "title": f"Retrieved {len(matched_metrics)} Certified Metrics & Schema Context",
        "status": "completed",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "matched_metrics": [m["name"] for m in matched_metrics],
            "context_tables": list(schema_context["tables"].keys())
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    return {
        "matched_metrics": matched_metrics,
        "schema_context": schema_context,
        "trace": trace
    }
