"""
InsightAgent FastAPI Route Endpoints
Provides POST /query, real-time SSE streaming GET /stream, GET /metrics, and GET /health.
"""

import json
import uuid
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Query as QueryParam
from fastapi.responses import StreamingResponse
from backend.api.schemas import QueryRequest, QueryResponse
from backend.graph.workflow import agent_runner
from backend.graph.state import AgentState
from backend.services.semantic_search import retriever
from mcp_server.tools.schema_tools import list_tables
from mcp_server.db import engine

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check for API, database, and schema accessibility."""
    try:
        tables = list_tables()
        return {
            "status": "healthy",
            "database_dialect": engine.dialect.name,
            "tables_found": len(tables),
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


@router.get("/metrics")
def get_metrics_catalog():
    """Returns the parsed semantic metrics catalog for the frontend drawer."""
    return {
        "metrics": retriever.metrics,
        "schema_metadata": retriever.schema_metadata
    }


@router.post("/admin/seed")
def seed_database(clients_count: int = 10000, orders_count: int = 100000):
    """
    Seeds the connected database (Postgres or SQLite) with capital markets data and anomalies.
    """
    from database.seed import init_schema, generate_clients, bulk_insert, generate_instruments, generate_orders_and_trades
    try:
        init_schema(engine)
        clients = generate_clients(n=clients_count)
        bulk_insert(engine, "clients", clients)
        instruments = generate_instruments()
        bulk_insert(engine, "instruments", instruments)
        orders, trades = generate_orders_and_trades(clients, instruments, target_orders=orders_count)
        bulk_insert(engine, "orders", orders)
        bulk_insert(engine, "trades", trades)
        tables = list_tables()
        return {
            "status": "success",
            "message": "Database schema initialized and seeded successfully.",
            "tables": tables,
            "clients_seeded": len(clients),
            "orders_seeded": len(orders),
            "trades_seeded": len(trades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def execute_query(req: QueryRequest):
    """Executes natural language query through the LangGraph pipeline synchronously."""
    query_id = str(uuid.uuid4())[:8]
    initial_state: AgentState = {
        "query_id": query_id,
        "user_query": req.query,
        "session_id": req.session_id,
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

    try:
        # Run graph in thread pool to avoid blocking async event loop
        final_state = await asyncio.to_thread(agent_runner.invoke, initial_state)
        return QueryResponse(
            query_id=query_id,
            user_query=req.query,
            intent=final_state.get("intent", "simple_query"),
            narrative_summary=final_state.get("narrative_summary", ""),
            chart_config=final_state.get("chart_config"),
            generated_sql=final_state.get("generated_sql", []),
            trace=final_state.get("trace", []),
            analytics_summary=final_state.get("analytics_results", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_query(q: str = QueryParam(..., description="User prompt"), session_id: str = "default_session"):
    """
    Real-time Server-Sent Events (SSE) streaming endpoint.
    Emits progress events for each LangGraph node execution and finishes with the final payload.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        query_id = str(uuid.uuid4())[:8]
        initial_state: AgentState = {
            "query_id": query_id,
            "user_query": q,
            "session_id": session_id,
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

        yield f"event: start\ndata: {json.dumps({'query_id': query_id, 'user_query': q})}\n\n"

        # Stream node execution using agent_runner.stream
        current_state = initial_state
        last_trace_len = 0

        for output_chunk in agent_runner.stream(current_state, stream_mode="updates"):
            # Each chunk is {node_name: updated_state_dict}
            for node_name, node_update in output_chunk.items():
                traces = node_update.get("trace", [])
                if len(traces) > last_trace_len:
                    for new_step in traces[last_trace_len:]:
                        step_data = {
                            "query_id": query_id,
                            "node": node_name,
                            "step": new_step
                        }
                        yield f"event: trace_step\ndata: {json.dumps(step_data)}\n\n"
                    last_trace_len = len(traces)

                # Keep merged state
                current_state.update(node_update)
            await asyncio.sleep(0.05)

        # Final complete payload event
        final_payload = {
            "query_id": query_id,
            "user_query": q,
            "intent": current_state.get("intent", "simple_query"),
            "narrative_summary": current_state.get("narrative_summary", ""),
            "chart_config": current_state.get("chart_config"),
            "generated_sql": current_state.get("generated_sql", []),
            "trace": current_state.get("trace", []),
            "analytics_summary": current_state.get("analytics_results", {})
        }
        yield f"event: result\ndata: {json.dumps(final_payload)}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
