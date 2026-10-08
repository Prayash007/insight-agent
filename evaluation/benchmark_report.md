# InsightAgent Golden Evaluation Benchmark Report

- **Date:** 2026-10-08 23:04:31 UTC
- **Target Domain:** Angel One Capital Markets & Retail Broking
- **Total Golden Queries:** 60
- **Database Scale:** 25,000 Clients | 250,000 Orders | 233,333 Trade Executions

## Key Performance Indicators

| Metric | Score | Target | Status |
| :--- | :--- | :--- | :--- |
| **Execution Success Rate (ESR)** | **100.0%** | $\ge 95\%$ | PASS |
| **Dataframe Equivalence (DFE)** | **100.0%** | $\ge 90\%$ | PASS |
| **Average Query Latency** | **619.9 ms** | $< 2500$ ms | PASS |
| **P95 Execution Latency** | **1292.4 ms** | $< 2500$ ms | PASS |

## Tier Performance Breakdown

| Tier | Total | Succeeded | Success Rate |
| :--- | :--- | :--- | :--- |
| **Tier 1: Single Filter & Aggregation** | 12 | 12 | 100.0% |
| **Tier 2: Multi-Table Joins** | 12 | 12 | 100.0% |
| **Tier 3: Time-Series & Trends** | 12 | 12 | 100.0% |
| **Tier 4: Semantic Metric Store** | 12 | 12 | 100.0% |
| **Tier 5: Diagnostic Root-Cause** | 12 | 12 | 100.0% |

## Flagship Scenarios Verified
1. **August F&O Contraction Investigation**: Decomposes July vs August turnover contraction (-34.7% drop), isolates index options (`OPTIDX`), and computes exact dimensional contribution share.
2. **August 14 Peak Margin Spike**: Pinpoints the 14x surge in `RMS_INSUFFICIENT_MARGIN` order rejections (36.4% on 2024-08-14 vs 2.8% baseline).
3. **Thursday Weekly Expiry Volume Concentration**: Detects 2.37x turnover surge on Thursdays representing over 38% of total weekly retail option trading volume.
