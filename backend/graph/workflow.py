"""
InsightAgent LangGraph Workflow Builder
Assembles the cyclic agent state machine with AST safety validation,
MCP query execution, self-correction retry loops, and deterministic Pandas analytics.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from backend.graph.state import AgentState
from backend.graph.nodes.router import router_node
from backend.graph.nodes.retriever import retriever_node
from backend.graph.nodes.planner import planner_node
from backend.graph.nodes.sql_generator import sql_generator_node
from backend.graph.nodes.validator_node import validator_node
from backend.graph.nodes.executor import executor_node
from backend.graph.nodes.analytics import analytics_node
from backend.graph.nodes.synthesizer import synthesizer_node
from backend.config import settings


def condition_after_planner(state: AgentState) -> Literal["synthesizer", "sql_generator"]:
    """Routes metric lookups directly to synthesis, and analytical questions to SQL generation."""
    if state.get("intent") == "metric_lookup":
        return "synthesizer"
    return "sql_generator"


def condition_after_validator(state: AgentState) -> Literal["sql_generator", "executor"]:
    """Self-correction loop: if AST check failed and retry_count < MAX_RETRIES, retry SQL generation."""
    error = state.get("error_context")
    retries = state.get("retry_count", 0)
    if error and "AST" in error and retries <= settings.MAX_SQL_RETRIES:
        return "sql_generator"
    return "executor"


def condition_after_executor(state: AgentState) -> Literal["sql_generator", "analytics"]:
    """Self-correction loop: if SQL execution failed and retry_count < MAX_RETRIES, retry SQL generation."""
    error = state.get("error_context")
    retries = state.get("retry_count", 0)
    if error and "Database" in error and retries <= settings.MAX_SQL_RETRIES:
        return "sql_generator"
    return "analytics"


def create_agent_graph():
    """Builds and compiles the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    # 1. Add All Graph Nodes
    graph.add_node("router", router_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("planner", planner_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("sql_validator", validator_node)
    graph.add_node("executor", executor_node)
    graph.add_node("analytics", analytics_node)
    graph.add_node("synthesizer", synthesizer_node)

    # 2. Add Standard Transitions
    graph.add_edge(START, "router")
    graph.add_edge("router", "retriever")
    graph.add_edge("retriever", "planner")

    # 3. Add Conditional Transitions
    graph.add_conditional_edges(
        "planner",
        condition_after_planner,
        {
            "synthesizer": "synthesizer",
            "sql_generator": "sql_generator"
        }
    )

    graph.add_edge("sql_generator", "sql_validator")

    graph.add_conditional_edges(
        "sql_validator",
        condition_after_validator,
        {
            "sql_generator": "sql_generator",
            "executor": "executor"
        }
    )

    graph.add_conditional_edges(
        "executor",
        condition_after_executor,
        {
            "sql_generator": "sql_generator",
            "analytics": "analytics"
        }
    )

    graph.add_edge("analytics", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


# Compile default runnable graph
agent_runner = create_agent_graph()
