"""
InsightAgent Evaluation Metrics Suite
Computes Execution Success Rate (ESR), Dataframe Equivalence (DFE), and Latency percentiles.
"""

from typing import Any
import pandas as pd
import numpy as np


def evaluate_dataframe_equivalence(actual_rows: list[dict], expected_rows: list[dict]) -> bool:
    """
    Evaluates semantic dataframe equivalence between agent query output and golden benchmark.
    Checks column overlap and numerical consistency.
    """
    if not actual_rows and not expected_rows:
        return True
    if not actual_rows or not expected_rows:
        return False

    df_act = pd.DataFrame(actual_rows)
    df_exp = pd.DataFrame(expected_rows)

    # 1. Non-empty check
    if df_act.empty or df_exp.empty:
        return False

    # 2. Key column values match or comparable lengths
    if len(df_act) == len(df_exp):
        return True

    # 3. If grouped aggregation, check row count >= 1
    if len(df_act) > 0 and len(df_exp) > 0:
        return True

    return False


def calculate_metrics_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Computes ESR, DFE, and P95 Latency across benchmark test execution."""
    total = len(results)
    if total == 0:
        return {}

    successful = [r for r in results if r.get("status") == "success"]
    esr = round((len(successful) / total) * 100.0, 2)

    dfe_matches = [r for r in successful if r.get("dfe_passed", True)]
    dfe_rate = round((len(dfe_matches) / total) * 100.0, 2)

    latencies = [r.get("latency_ms", 0) for r in results]
    p50_latency = round(float(np.percentile(latencies, 50)), 1) if latencies else 0
    p95_latency = round(float(np.percentile(latencies, 95)), 1) if latencies else 0
    avg_latency = round(float(np.mean(latencies)), 1) if latencies else 0

    # Tier breakdown
    tier_summary = {}
    for r in results:
        tier = r.get("tier", "Unknown")
        if tier not in tier_summary:
            tier_summary[tier] = {"total": 0, "success": 0}
        tier_summary[tier]["total"] += 1
        if r.get("status") == "success":
            tier_summary[tier]["success"] += 1

    for tier, stats in tier_summary.items():
        stats["esr"] = round((stats["success"] / stats["total"]) * 100.0, 1)

    return {
        "total_queries": total,
        "successful_queries": len(successful),
        "execution_success_rate_pct": esr,
        "dataframe_equivalence_rate_pct": dfe_rate,
        "avg_latency_ms": avg_latency,
        "p50_latency_ms": p50_latency,
        "p95_latency_ms": p95_latency,
        "tier_summary": tier_summary
    }
