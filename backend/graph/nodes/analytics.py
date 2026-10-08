"""
InsightAgent LangGraph Node: Deterministic Analytics Engine (Pandas)
Offloads all mathematical computations, period-over-period (PoP) variances,
dimension contribution shares, and rolling aggregations to Pandas to eliminate LLM arithmetic hallucinations.
"""

import time
import uuid
from typing import Any
import pandas as pd
import numpy as np
from backend.graph.state import AgentState, TraceStep


def compute_pop_variance(df: pd.DataFrame, metric_col: str, time_col: str) -> dict[str, Any]:
    """Computes exact Period-over-Period (PoP) percentage and absolute delta."""
    if len(df) < 2:
        return {}
    
    # Sort chronologically
    sorted_df = df.sort_values(by=time_col)
    t0_val = float(sorted_df.iloc[-2][metric_col])
    t1_val = float(sorted_df.iloc[-1][metric_col])
    
    abs_delta = t1_val - t0_val
    pct_delta = ((abs_delta) / t0_val * 100.0) if t0_val != 0 else 0.0

    return {
        "baseline_period": str(sorted_df.iloc[-2][time_col]),
        "baseline_value": round(t0_val, 2),
        "target_period": str(sorted_df.iloc[-1][time_col]),
        "target_value": round(t1_val, 2),
        "absolute_change": round(abs_delta, 2),
        "percentage_change": round(pct_delta, 2)
    }


def compute_dimension_contributions(df: pd.DataFrame, dim_col: str, metric_col: str, time_col: str) -> list[dict[str, Any]]:
    """
    Computes exact percentage contribution of each dimension to total period variance:
      Contribution % = (Delta_dim / Delta_total) * 100
    """
    if dim_col not in df.columns or metric_col not in df.columns or time_col not in df.columns:
        return []

    pivoted = df.pivot_table(index=dim_col, columns=time_col, values=metric_col, fill_value=0)
    if pivoted.shape[1] < 2:
        return []

    t0_col, t1_col = pivoted.columns[-2], pivoted.columns[-1]
    deltas = pivoted[t1_col] - pivoted[t0_col]
    total_delta = deltas.sum()

    contributions = []
    for dim_val, delta in deltas.items():
        share = (delta / total_delta * 100.0) if total_delta != 0 else 0.0
        contributions.append({
            "dimension": str(dim_val),
            "baseline_value": round(float(pivoted.loc[dim_val, t0_col]), 2),
            "target_value": round(float(pivoted.loc[dim_val, t1_col]), 2),
            "delta": round(float(delta), 2),
            "contribution_pct": round(float(share), 2)
        })

    # Sort by absolute delta
    contributions.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return contributions


def analyze_query_results(user_query: str, intent: str, query_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Runs deterministic statistical and variance calculations over query outputs."""
    analytics = {
        "summary_metrics": {},
        "pop_analysis": {},
        "dimension_breakdown": [],
        "kpis": [],
        "table_data": []
    }

    if not query_results or not query_results[0].get("rows"):
        return analytics

    # Primary DataFrame
    primary_res = query_results[0]
    df_primary = pd.DataFrame(primary_res.get("rows", []))
    analytics["table_data"] = primary_res.get("rows", [])

    # 1. PoP Analysis for monthly time-series
    if "month" in df_primary.columns and "total_turnover" in df_primary.columns:
        pop = compute_pop_variance(df_primary, metric_col="total_turnover", time_col="month")
        analytics["pop_analysis"] = pop
        if pop:
            analytics["kpis"].append({
                "label": f"F&O Turnover ({pop.get('target_period')})",
                "value": f"₹{pop.get('target_value', 0):,.2f}",
                "delta": f"{pop.get('percentage_change')}%",
                "status": "negative" if pop.get("percentage_change", 0) < 0 else "positive"
            })

    # 2. Multi-dimensional contribution breakdown (for Diagnostic "Why" queries)
    if intent == "diagnostic_why" and len(query_results) > 1:
        # Check second query for instrument_type breakdown
        df_dim = pd.DataFrame(query_results[1].get("rows", []))
        if "instrument_type" in df_dim.columns and "turnover" in df_dim.columns and "month" in df_dim.columns:
            dim_contrib = compute_dimension_contributions(df_dim, "instrument_type", "turnover", "month")
            analytics["dimension_breakdown"] = dim_contrib

    # 3. RMS Rejection Spike Analysis
    if "rms_rejection_rate_pct" in df_primary.columns or "rms_rejections" in df_primary.columns:
        if "rms_rejection_rate_pct" in df_primary.columns:
            peak_row = df_primary.loc[df_primary["rms_rejection_rate_pct"].astype(float).idxmax()]
            baseline_avg = df_primary["rms_rejection_rate_pct"].astype(float).median()
            peak_val = float(peak_row["rms_rejection_rate_pct"])
            surge_mult = round(peak_val / baseline_avg, 1) if baseline_avg > 0 else 1.0

            analytics["summary_metrics"]["rms_peak_date"] = str(peak_row.get("order_date"))
            analytics["summary_metrics"]["rms_peak_rate_pct"] = peak_val
            analytics["summary_metrics"]["rms_baseline_median_pct"] = round(baseline_avg, 2)
            analytics["summary_metrics"]["rms_surge_multiplier"] = surge_mult

            analytics["kpis"].append({
                "label": f"Peak RMS Rejection ({peak_row.get('order_date')})",
                "value": f"{peak_val}%",
                "delta": f"{surge_mult}x spike vs baseline",
                "status": "negative"
            })

    # 4. Thursday vs Weekday Options Analysis
    if "weekday" in df_primary.columns and "total_turnover" in df_primary.columns:
        thurs_rows = df_primary[df_primary["weekday"].str.strip().str.lower() == "thursday"]
        other_rows = df_primary[df_primary["weekday"].str.strip().str.lower() != "thursday"]
        if not thurs_rows.empty and not other_rows.empty:
            thurs_val = float(thurs_rows["total_turnover"].iloc[0])
            avg_others = float(other_rows["total_turnover"].mean())
            mult = round(thurs_val / avg_others, 2) if avg_others > 0 else 1.0
            share_pct = round(thurs_val / df_primary["total_turnover"].sum() * 100.0, 2)

            analytics["summary_metrics"]["thursday_surge_multiplier"] = mult
            analytics["summary_metrics"]["thursday_volume_share_pct"] = share_pct

            analytics["kpis"].append({
                "label": "Thursday Weekly Expiry Volume",
                "value": f"₹{thurs_val:,.2f}",
                "delta": f"{mult}x vs other weekdays",
                "status": "positive"
            })

    # 5. Order Fill Rate
    if "fill_rate_pct" in df_primary.columns:
        overall_fill = round(float(df_primary["fill_rate_pct"].mean()), 2)
        analytics["kpis"].append({
            "label": "Average Order Fill Rate",
            "value": f"{overall_fill}%",
            "delta": "Across order types",
            "status": "positive" if overall_fill >= 90 else "neutral"
        })

    return analytics


def analytics_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    user_query = state.get("user_query", "")
    intent = state.get("intent", "simple_query")
    query_results = state.get("query_results", [])

    analytics_results = analyze_query_results(user_query, intent, query_results)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "analytics",
        "title": "Deterministic Calculations Complete (Pandas)",
        "status": "completed",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "kpis_computed": len(analytics_results.get("kpis", [])),
            "pop_available": bool(analytics_results.get("pop_analysis")),
            "dimensions_analyzed": len(analytics_results.get("dimension_breakdown", []))
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    return {
        "analytics_results": analytics_results,
        "trace": trace
    }
