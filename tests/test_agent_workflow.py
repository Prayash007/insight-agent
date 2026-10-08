"""
Integration Tests: LangGraph Cyclic Workflow & Deterministic Analytics Engine
"""

import pytest
from backend.graph.workflow import agent_runner
from backend.graph.state import AgentState


def test_flagship_why_fno_drop():
    initial_state: AgentState = {
        "query_id": "test_q1",
        "user_query": "Why did F&O volume drop in August?",
        "session_id": "sess_1",
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
        "error_context": None,
        "retry_count": 0,
        "trace": []
    }

    final_state = agent_runner.invoke(initial_state)

    assert final_state["intent"] == "diagnostic_why"
    assert len(final_state["plan"]) >= 3
    assert len(final_state["generated_sql"]) >= 3
    assert all(r["is_valid"] for r in final_state["ast_validation_results"])
    assert len(final_state["query_results"]) >= 3
    assert "pop_analysis" in final_state["analytics_results"]
    assert final_state["chart_config"] is not None
    assert "Executive Analytical Briefing" in final_state["narrative_summary"]
    assert len(final_state["trace"]) >= 7


def test_flagship_august_14_rms_spike():
    initial_state: AgentState = {
        "query_id": "test_q2",
        "user_query": "What caused the spike in RMS margin rejections on August 14?",
        "session_id": "sess_2",
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
        "error_context": None,
        "retry_count": 0,
        "trace": []
    }

    final_state = agent_runner.invoke(initial_state)

    assert len(final_state["generated_sql"]) >= 1
    assert any("order_date" in str(r.get("columns", [])) for r in final_state["query_results"])
    summary_metrics = final_state["analytics_results"].get("summary_metrics", {})
    assert "rms_peak_rate_pct" in summary_metrics
    assert summary_metrics["rms_peak_rate_pct"] > 25.0
    assert "RMS_INSUFFICIENT_MARGIN" in final_state["narrative_summary"]


def test_flagship_thursday_expiry_surge():
    initial_state: AgentState = {
        "query_id": "test_q3",
        "user_query": "Compare Thursday expiry turnover against other weekdays",
        "session_id": "sess_3",
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
        "error_context": None,
        "retry_count": 0,
        "trace": []
    }

    final_state = agent_runner.invoke(initial_state)

    summary_metrics = final_state["analytics_results"].get("summary_metrics", {})
    assert "thursday_surge_multiplier" in summary_metrics
    assert summary_metrics["thursday_surge_multiplier"] >= 2.0
    assert final_state["chart_config"]["chart_type"] == "bar"
