"""
InsightAgent LangGraph Node: Executive Synthesizer & Chart Spec Generator
Transforms deterministic statistical outputs into an institutional executive summary
and builds a declarative Recharts JSON configuration for frontend rendering.
"""

import time
import uuid
from typing import Any
from backend.graph.state import AgentState, TraceStep


def generate_chart_config(intent: str, analytics: dict[str, Any], query_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Builds a declarative Recharts specification matching frontend ChartRenderer contract."""
    kpi_cards = analytics.get("kpis", [])
    table_data = analytics.get("table_data", [])

    if not table_data:
        return {
            "chart_type": "kpi_grid",
            "title": "Analytical Summary",
            "kpi_cards": kpi_cards,
            "data": []
        }

    sample_row = table_data[0]
    keys = list(sample_row.keys())

    # Case 1: Diagnostic Why (Instrument Type Breakdown or PoP)
    if intent == "diagnostic_why" and analytics.get("dimension_breakdown"):
        dim_data = analytics.get("dimension_breakdown")
        return {
            "chart_type": "bar",
            "title": "Turnover Variance Contribution by Instrument Type (July vs August)",
            "x_key": "dimension",
            "y_keys": ["delta", "contribution_pct"],
            "series_labels": {
                "delta": "Turnover Delta (INR)",
                "contribution_pct": "Contribution Share (%)"
            },
            "kpi_cards": kpi_cards,
            "data": dim_data
        }

    # Case 2: Time Series / Date (e.g. RMS spike or monthly trend)
    if any(k in keys for k in ["order_date", "trade_date", "month"]):
        date_col = next(k for k in keys if k in ["order_date", "trade_date", "month"])
        numeric_cols = [k for k in keys if k != date_col and isinstance(sample_row[k], (int, float))]
        chart_type = "line" if len(table_data) > 3 else "bar"
        return {
            "chart_type": chart_type,
            "title": "Trend & Anomaly Analysis",
            "x_key": date_col,
            "y_keys": numeric_cols[:2],
            "series_labels": {col: col.replace("_", " ").title() for col in numeric_cols[:2]},
            "kpi_cards": kpi_cards,
            "data": table_data
        }

    # Case 3: Weekday Breakdown (Thursday Expiry)
    if "weekday" in keys:
        numeric_cols = [k for k in keys if k != "weekday" and isinstance(sample_row[k], (int, float))]
        return {
            "chart_type": "bar",
            "title": "F&O Options Turnover by Weekday (Expiry Day Concentration)",
            "x_key": "weekday",
            "y_keys": ["total_turnover"] if "total_turnover" in keys else numeric_cols[:1],
            "series_labels": {
                "total_turnover": "Total Turnover (INR)",
                "trade_count": "Trades Executed"
            },
            "kpi_cards": kpi_cards,
            "data": table_data
        }

    # Case 4: Category / Dimension (e.g., segment, tier, order_type)
    cat_candidates = ["segment", "tier", "order_type", "rejection_reason", "zone"]
    cat_col = next((c for c in cat_candidates if c in keys), keys[0])
    numeric_cols = [k for k in keys if k != cat_col and isinstance(sample_row[k], (int, float))]

    return {
        "chart_type": "bar",
        "title": f"Distribution by {cat_col.replace('_', ' ').title()}",
        "x_key": cat_col,
        "y_keys": numeric_cols[:2] if numeric_cols else [],
        "series_labels": {col: col.replace("_", " ").title() for col in numeric_cols[:2]},
        "kpi_cards": kpi_cards,
        "data": table_data
    }


def synthesize_narrative(user_query: str, intent: str, analytics: dict[str, Any], state: AgentState) -> str:
    """Synthesizes structured capital markets executive takeaways using Gemini or deterministic engine."""
    from backend.services.llm import llm_service
    import json

    # If Cloud LLM (Gemini / OpenAI) is configured, use it for narrative synthesis
    if llm_service.get_active_provider() != "deterministic":
        prompt = f"""You are InsightAgent, an autonomous Capital Markets AI Data Analyst for Angel One.
Review the following deterministic statistical findings computed by Python/Pandas and write an institutional executive briefing:

User Query: {user_query}
Intent: {intent}

Deterministic Analytics Computed by Pandas:
- Period-over-Period (PoP): {json.dumps(analytics.get('pop_analysis', {}))}
- Dimensional Contributions: {json.dumps(analytics.get('dimension_breakdown', []))}
- Key KPIs: {json.dumps(analytics.get('kpis', []))}
- Summary Metrics: {json.dumps(analytics.get('summary_metrics', {}))}

Instructions:
1. Provide a clear Executive Analytical Briefing.
2. Emphasize the exact percentage changes and primary drivers.
3. If investigating August F&O volume drop, explain the options IV drop and SEBI lot-size factors.
4. If investigating August 14 RMS rejection spike, explain the BankNifty gap-down and peak margin snapshot breaches.
5. If analyzing Thursdays, explain the weekly NSE/BSE contract expiry concentration.
6. Note explicitly that all mathematical figures were verified deterministically via Pandas.
"""
        llm_response = llm_service.generate(prompt, system_prompt="You are an institutional financial analyst at Angel One.")
        if llm_response:
            return llm_response

    # Deterministic fallback synthesis
    matched = state.get("matched_metrics", [])
    metric_name = matched[0]["name"] if matched else "Metric"
    pop = analytics.get("pop_analysis", {})
    kpis = analytics.get("kpis", [])
    dim_breakdown = analytics.get("dimension_breakdown", [])
    summary_metrics = analytics.get("summary_metrics", {})

    lines = []
    lines.append(f"### Executive Analytical Briefing")
    lines.append(f"**Query Focus:** *{user_query}*\n")

    # Flagship Anomaly 1: August F&O Contraction
    if pop and "total_turnover" in pop.get("target_period", "") or pop.get("percentage_change"):
        pct = pop.get("percentage_change", 0)
        lines.append(f"**Period-over-Period Performance:**")
        lines.append(f"- **Baseline ({pop.get('baseline_period')}):** ₹{pop.get('baseline_value', 0):,.2f}")
        lines.append(f"- **Target ({pop.get('target_period')}):** ₹{pop.get('target_value', 0):,.2f}")
        lines.append(f"- **Net Variance:** ₹{pop.get('absolute_change', 0):,.2f} (**{pct:+.2f}%**)")
        lines.append("")

        if dim_breakdown:
            lines.append("**Dimensional Contribution Drivers:**")
            for d in dim_breakdown[:3]:
                lines.append(f"- **{d['dimension']}:** Delta of ₹{d['delta']:,.2f} ({d['contribution_pct']:.1f}% share of total variance)")
            lines.append("")

    # Flagship Anomaly 2: August 14 RMS Rejection Spike
    if "rms_peak_date" in summary_metrics:
        peak_date = summary_metrics["rms_peak_date"]
        peak_pct = summary_metrics["rms_peak_rate_pct"]
        baseline_pct = summary_metrics["rms_baseline_median_pct"]
        mult = summary_metrics["rms_surge_multiplier"]
        lines.append(f"**RMS Risk Rejection Investigation:**")
        lines.append(f"- **Acute Anomaly Detected:** Order rejections surged to **{peak_pct}%** on **{peak_date}** (vs baseline median of **{baseline_pct}%**).")
        lines.append(f"- **Surge Magnitude:** **{mult}x** elevation above normal risk tolerance thresholds.")
        lines.append(f"- **Root Cause:** Intraday peak margin snapshot requirements during sharp BankNifty index drop triggered widespread `RMS_INSUFFICIENT_MARGIN` rejections on retail market and limit orders.")
        lines.append("")

    # Flagship Anomaly 3: Thursday Expiry Volume Surge
    if "thursday_surge_multiplier" in summary_metrics:
        mult = summary_metrics["thursday_surge_multiplier"]
        share = summary_metrics["thursday_volume_share_pct"]
        lines.append(f"**Weekly Expiry Volume Dynamics:**")
        lines.append(f"- **Thursday Expiry Concentration:** Thursday options turnover outpaces other weekdays by **{mult}x**.")
        lines.append(f"- **Share of Weekly Turnover:** Thursday scalping and zero-DTE options account for **{share}%** of all weekly options trading value.")
        lines.append("")

    # General KPIs
    if kpis:
        lines.append("**Key Performance Indicators:**")
        for k in kpis:
            lines.append(f"- **{k['label']}:** {k['value']} ({k.get('delta', '')})")
        lines.append("")

    lines.append("*All statistical aggregations, percentages, and deltas calculated deterministically via Python/Pandas engine.*")
    return "\n".join(lines)


def synthesizer_node(state: AgentState) -> dict:
    start_time = time.perf_counter()
    user_query = state.get("user_query", "")
    intent = state.get("intent", "simple_query")
    analytics_results = state.get("analytics_results", {})
    query_results = state.get("query_results", [])

    narrative = synthesize_narrative(user_query, intent, analytics_results, state)
    chart_config = generate_chart_config(intent, analytics_results, query_results)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    step: TraceStep = {
        "step_id": str(uuid.uuid4())[:8],
        "node": "synthesizer",
        "title": "Generated Executive Narrative & Recharts Spec",
        "status": "completed",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_ms": elapsed_ms,
        "details": {
            "narrative_length": len(narrative),
            "chart_type": chart_config.get("chart_type") if chart_config else None
        }
    }

    trace = list(state.get("trace", []))
    trace.append(step)

    return {
        "narrative_summary": narrative,
        "chart_config": chart_config,
        "trace": trace
    }
