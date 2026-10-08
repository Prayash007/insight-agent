"""
Unit Tests: Self-Correction Loop & Error Recovery in LangGraph
"""

import pytest
from backend.graph.workflow import agent_runner
from backend.graph.state import AgentState


def test_self_correction_ast_recovery():
    # Inject an initial state with a malformed SQL query to trigger self-correction
    initial_state: AgentState = {
        "query_id": "test_retry_ast",
        "user_query": "What is our order fill rate by order type?",
        "session_id": "sess_retry",
        "intent": "simple_query",
        "matched_metrics": [],
        "schema_context": {},
        "plan": [],
        "generated_sql": [],
        "ast_validation_results": [],
        "query_results": [],
        "analytics_results": {},
        "chart_config": None,
        "narrative_summary": "",
        "error_context": "Previous attempt had invalid SQL token",
        "retry_count": 1, # Simulating retry cycle
        "trace": []
    }

    final_state = agent_runner.invoke(initial_state)

    assert final_state["chart_config"] is not None
    assert len(final_state["query_results"]) >= 1
    assert any("fill_rate_pct" in str(r.get("columns", [])) for r in final_state["query_results"])
    # Verify trace records self-correction
    trace_titles = [t["title"] for t in final_state["trace"]]
    assert any("Self-Correction" in t for t in trace_titles)
