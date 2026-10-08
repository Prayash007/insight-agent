# InsightAgent 📈
### Autonomous Capital Markets AI Data Analyst for Angel One
> **Production-grade LangGraph Orchestration • Decoupled FastMCP (SSE) • sqlglot AST Query Guardrails • Deterministic Pandas Analytics**

[![Vercel Deployment](https://img.shields.io/badge/Vercel-insight--agent--iota.vercel.app-black?logo=vercel&logoColor=white)](https://insight-agent-iota.vercel.app/)
[![Render Backend](https://img.shields.io/badge/Render-API%20Gateway-46E3B7?logo=render&logoColor=white)](https://insight-agent-backend-goe0.onrender.com)
[![Database](https://img.shields.io/badge/PostgreSQL%2016-Render%20Managed-336791?logo=postgresql&logoColor=white)](https://dashboard.render.com/d/dpg-db3u6cub7d7c739l9k7g-a)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Prayash007%2Finsight--agent-181717?logo=github&logoColor=white)](https://github.com/Prayash007/insight-agent)
[![Benchmark ESR](https://img.shields.io/badge/Benchmark_ESR-100%25_(60%2F60)-emerald.svg)](./evaluation/benchmark_report.md)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![FastMCP](https://img.shields.io/badge/Protocol-Model_Context_Protocol_(SSE)-purple.svg)](https://modelcontextprotocol.io/)

## 🌐 Live Cloud Deployment & Infrastructure Links

| Resource | Service / Provider | Live URL / Endpoint | Purpose & Functionality |
| :--- | :--- | :--- | :--- |
| **Interactive Web Dashboard** | **Vercel Edge** | [insight-agent-iota.vercel.app](https://insight-agent-iota.vercel.app/) | React 19 + TypeScript analytics UI, real-time SSE execution trace accordion, dynamic Recharts visualizations |
| **Production API Gateway** | **Render Web Service** | [insight-agent-backend-goe0.onrender.com](https://insight-agent-backend-goe0.onrender.com) | FastAPI + LangGraph cyclic state machine + sqlglot AST guardrails + deterministic Pandas engine |
| **Interactive API Documentation** | **Swagger / OpenAPI** | [insight-agent-backend-goe0.onrender.com/docs](https://insight-agent-backend-goe0.onrender.com/docs) | Interactive endpoint contracts (`POST /api/query`, `GET /api/stream`, `POST /api/admin/seed`, `GET /api/metrics`) |
| **Production Managed Database** | **Render PostgreSQL 16** | [Render Database Instance](https://dashboard.render.com/d/dpg-db3u6cub7d7c739l9k7g-a) | Managed capital markets relational store populated with 25,000 clients and 250,000 orders/trades |
| **Source Code Repository** | **GitHub** | [github.com/Prayash007/insight-agent](https://github.com/Prayash007/insight-agent) | Public monorepo with automated golden query benchmarks, Docker Compose, and FastMCP tooling |

---

## 1. Executive Summary & Engineering Motivation

Modern retail stockbrokers like **Angel One** process millions of daily orders across Equity Cash, Options, Futures, and Commodities. Traditional text-to-SQL wrappers are brittle and dangerous in production: they hallucinate financial formulas, produce unvalidated DML statements, and fail to diagnose multi-dimensional root causes (such as sudden volume contractions or margin rejection spikes).

Drawing on software engineering internship experience at **Microsoft**—where I engineered decoupled microservices and stateful agentic solutions—**InsightAgent** is designed as a resilient, enterprise-grade autonomous data analyst. It turns plain-English questions from product managers, risk teams, and executives into certified metrics, root-cause decompositions, and interactive Recharts visualizations without writing a line of SQL.

---

## 2. Cloud Architecture & Live Interconnection

InsightAgent is deployed across a decoupled multi-cloud architecture ensuring edge performance, zero-leak credential isolation, and resilient real-time streaming:

```mermaid
flowchart LR
    subgraph ClientLayer["Edge / Client Layer (Vercel)"]
        Browser["User Browser"]
        VercelEdge["Vercel Edge CDN<br/>(insight-agent-iota.vercel.app)"]
        VercelProxy["Edge Rewrite Rule<br/>/api/* &rarr; Render"]
    end

    subgraph ServiceLayer["Application Layer (Render Oregon)"]
        FastAPIApp["FastAPI Gateway (Port 8000)<br/>CORS: Allow All / Credentials"]
        LangGraphEng["LangGraph Stateful Agent<br/>(Cyclic Self-Correction)"]
        PandasEng["Deterministic Pandas<br/>Analytics Engine"]
        AdminSeed["One-Click Seeder<br/>POST /api/admin/seed"]
    end

    subgraph DataLayer["Persistence Layer (Render PostgreSQL)"]
        FastMCPServer["FastMCP Read-Only Pool<br/>(2500ms Statement Timeout)"]
        PostgresDB[("PostgreSQL 16 Instance<br/>insight-brokerage-db<br/>(25k Clients / 250k Trades)")]
    end

    Browser -->|HTTPS :443| VercelEdge
    VercelEdge --> Browser
    Browser -->|API Requests & SSE Stream| VercelProxy
    VercelProxy -->|Transparent Reverse Proxy| FastAPIApp
    FastAPIApp --> LangGraphEng
    LangGraphEng --> FastMCPServer
    FastMCPServer -->|psycopg SSL Pool| PostgresDB
    FastMCPServer -->|Raw RecordBatches| PandasEng
    PandasEng --> LangGraphEng
    AdminSeed -->|Bulk DDL & Synthetic Data| PostgresDB
    FastAPIApp -.->|SSE Trace Stream /api/stream| Browser
```

### How the Cloud Services Connect

1. **Vercel Frontend to Render Backend Bridge:**
   - Configured via [`frontend/vercel.json`](file:///D:/Practical/Agentic_AI_Project/frontend/vercel.json):
     ```json
     {
       "framework": "vite",
       "buildCommand": "npm run build",
       "outputDirectory": "dist",
       "rewrites": [
         {
           "source": "/api/:path*",
           "destination": "https://insight-agent-backend-goe0.onrender.com/api/:path*"
         }
       ]
     }
     ```
   - **Zero-CORS Reverse Proxy:** Because the frontend routes `/api/*` through Vercel's edge network, the browser sends requests to the same origin (`insight-agent-iota.vercel.app/api/*`). This eliminates cross-origin preflight overhead and prevents browser ad-blockers or CORS policies from severing long-lived Server-Sent Events (SSE) connections.
   - **Environment Variable Fallback:** The Vite client also honors `VITE_API_BASE_URL` if configured for custom backend deployments.

2. **Render Backend to Managed PostgreSQL 16:**
   - The FastAPI backend connects to the managed PostgreSQL 16 database via the environment variable `DATABASE_URL` (`postgresql+psycopg://...`).
   - The connection pool operates with forced SSL (`sslmode=require`), `statement_timeout = '2500ms'`, and AST query validation (`sqlglot`) to strictly guarantee read-only data access.

3. **Cloud Database Seeding & Schema Population:**
   The cloud database can be initialized and loaded with 25k clients and 250k trades via either of two methods:
   - **Method A: One-Click Admin Seed Endpoint (Recommended)**
     Run an HTTP POST request directly against the deployed backend:
     ```bash
     curl -X POST "https://insight-agent-backend-goe0.onrender.com/api/admin/seed?clients_count=10000&orders_count=100000"
     ```
     *Or open the [Interactive Swagger Docs](https://insight-agent-backend-goe0.onrender.com/docs#/default/seed_database_api_admin_seed_post) and click "Try it out" &rarr; "Execute".*
   - **Method B: CLI Direct Seed via External Connection URL**
     From your local machine, run the synthetic capital markets generator passing your Render external database string:
     ```bash
     python database/seed.py --db-url "postgresql://insight_agent_db_user:<PASSWORD>@dpg-db3u6cub7d7c739l9k7g-a-a.oregon-postgres.render.com/insight_agent_db?sslmode=require"
     ```

4. **Cloud Environment Variable Configuration Reference:**
   | Service | Variable Name | Production Value / Description |
   | :--- | :--- | :--- |
   | **Render Backend** | `DATABASE_URL` | Render Managed Postgres Internal/External Connection URI (`postgresql+psycopg://...`) |
   | **Render Backend** | `GEMINI_API_KEY` | Google Gemini API Key for autonomous query planning and synthesis |
   | **Render Backend** | `DEFAULT_MODEL` | `gemini-3-flash-preview` or `gemini-2.5-flash` |
   | **Render Backend** | `MCP_USE_IN_PROCESS` | `true` (enables low-latency in-process MCP execution) |
   | **Render Backend** | `PORT` | Auto-configured by Render (`8000` default) |
   | **Vercel Frontend** | `VITE_API_BASE_URL` | *(Optional)* Defaults to `/api` proxy rewrite |

---

## 3. Core Architectural Pillars

```mermaid
flowchart TD
    subgraph UI["Interactive Frontend (React 19 + TypeScript + Recharts)"]
        Chat[Prompt Bar with Flagship Scenarios]
        Trace[Real-Time Execution Trace SSE]
        Chart[Dynamic Recharts: Line / Bar / Area / KPIs]
        SQLBox[AST Inspector & Badges]
        Drawer[Semantic Catalog Drawer]
    end

    subgraph Backend["FastAPI Backend (Port 8000)"]
        Router[1. Intent Router: Simple vs Diagnostic 'Why']
        Retriever[2. Semantic Catalog Retriever]
        Planner[3. Multi-Query Dimensional Decomposition]
        SQLGen[4. Dialect-Aware SQL Generator]
        SQLVal[5. sqlglot AST Validator & Limit Guardrails]
        Analytics[6. Deterministic Pandas Engine]
        Synthesizer[7. Executive Narrative & Recharts Spec]
    end

    subgraph MCP["Decoupled FastMCP Server (SSE Transport, Port 8001)"]
        MCPServer[FastMCP Server]
        Tool1[list_schema]
        Tool2[get_metric_definition]
        Tool3[execute_readonly_sql]
        Tool4[explain_query]
        Pool[Read-Only Pool: 2500ms Statement Timeout]
    end

    subgraph DB["Capital Markets Database (250k Trades / 25k Clients)"]
        ClientsTbl[(clients)]
        InstrumentsTbl[(instruments)]
        OrdersTbl[(orders)]
        TradesTbl[(trades)]
    end

    Chat -->|Natural Language Prompt| Router
    Router --> Retriever
    Retriever --> Planner
    Planner --> SQLGen
    SQLGen --> SQLVal
    SQLVal -->|Valid AST| Tool3
    SQLVal -.->|AST Syntax Error| SQLGen
    Tool3 --> Pool --> DB
    Tool3 -.->|DB Runtime Error| SQLGen
    Tool3 -->|Raw RecordBatches| Analytics
    Analytics --> Synthesizer
    Synthesizer -->|SSE Stream| Trace
    Synthesizer -->|Chart JSON Spec| Chart
    SQLVal --> SQLBox
```

### 1. Semantic Router & Planner (Zero Mathematical Hallucination)
- Mathematical operations are **never** left to LLM guesswork.
- Before SQL generation, the agent queries `backend/catalog/metrics.yaml` for certified formulas:
  - **Order Fill Rate:** `COUNT(status = 'COMPLETE') / COUNT(*) * 100`
  - **RMS Rejection Rate:** `COUNT(status = 'REJECTED' AND rejection_reason = 'RMS_INSUFFICIENT_MARGIN') / COUNT(*) * 100`
  - **Average Brokerage Yield (bps):** `(SUM(brokerage_amount) / SUM(turnover)) * 10,000`
  - **F&O Turnover Contribution Share:** Derivatives turnover vs Total market turnover

### 2. Stateful Cyclic Orchestration with Self-Correction (LangGraph)
- Plans multi-query investigations and captures errors in explicit state.
- Features an internal **self-correction loop**: if an AST parse error or PostgreSQL runtime error occurs, the traceback is fed back into the SQL generator to automatically repair and retry (max 2 retries).

### 3. Decoupled FastMCP Server (SSE Transport)
- Database interactions run in an isolated process over the **Model Context Protocol (MCP)** using Server-Sent Events (SSE).
- Hardened database connection pool:
  - `default_transaction_read_only = on`
  - `statement_timeout = '2500ms'`
  - Exposed tools: `list_schema`, `get_metric_definition`, `execute_readonly_sql`, `explain_query`.

### 4. AST Validation Engine (`sqlglot`)
- Strict query guardrails:
  - Enforces that root AST node is strictly `Select` or `Union` (rejects `Insert`, `Update`, `Delete`, `Drop`, `Alter`).
  - Blocks access to administrative catalogs (`pg_catalog`, `information_schema`, `sqlite_master`).
  - Automatically injects `LIMIT 500` if omitted or clamps excessive limits.

### 5. Deterministic Analytics Engine (Pandas)
- Offloads all Period-over-Period (PoP) percentage changes, dimensional contribution percentages, and moving averages to Python/Pandas.
- The LLM is strictly reserved for narrative synthesis and dynamic UI configuration.

### 6. Diagnostic "Why" Engine
- Decomposes root-cause questions (e.g. *"Why did F&O volume drop last month?"*) into parallel dimensional queries:
  $$\text{Contribution } \% = \frac{\Delta \text{segment}}{\Delta \text{total}} \times 100$$
- Pinpoints the exact segment, client tier, and rejection reason driving performance variances.

---

## 4. High-Fidelity Capital Markets Database

Seeded with **25,000 clients** and **250,000 orders/trades** across 8 months, modeling three realistic capital market patterns:

| Anomaly Pattern | Target Metric | Business Reality Injected | Detected Anomaly |
| :--- | :--- | :--- | :--- |
| **August F&O Turnover Contraction** | `gross_turnover` | Volatility collapse (India VIX drop) and lot size revisions | **-34.7% contraction** in August options turnover |
| **August 14 Peak Margin Rejection Spike** | `rms_rejection_rate` | Sudden BankNifty intraday gap-down triggered exchange margin snapshot failures | **36.4% rejection spike** (451 margin rejections vs 2.8% baseline) |
| **Thursday Weekly Expiry Surges** | `daily_turnover` | Weekly NSE contract expiry scalp volume | **2.37x turnover concentration** on Thursdays |

---

## 5. Evaluation Benchmark Results (60 Golden Queries)

InsightAgent includes an automated benchmark runner (`evaluation/evaluate.py`) testing 60 capital-markets queries across 5 tiers:

| Benchmark Tier | Query Count | Passed | Success Rate (ESR) |
| :--- | :--- | :--- | :--- |
| **Tier 1: Single Filter & Aggregations** | 12 | 12 | **100.0%** |
| **Tier 2: Multi-Table Relational Joins** | 12 | 12 | **100.0%** |
| **Tier 3: Time-Series & Trend Analysis** | 12 | 12 | **100.0%** |
| **Tier 4: Semantic Metric Store Calculations** | 12 | 12 | **100.0%** |
| **Tier 5: Diagnostic Root-Cause ("Why")** | 12 | 12 | **100.0%** |
| **Overall Benchmark** | **60** | **60** | **100.0%** |

### Benchmark Latency Profile
- **Average Latency:** `619.9 ms`
- **P50 Latency:** `729.1 ms`
- **P95 Latency:** `1292.4 ms` (Well under the 2500ms enterprise SLA)
- **Dataframe Equivalence (DFE):** `100.0%`

---

## 6. Repository Structure

```
insight-agent/
├── docker-compose.yml                 # Multi-container orchestration (DB, MCP, Backend, Frontend)
├── .env.example                       # Environment template
├── README.md                          # Production engineering documentation
│
├── database/
│   ├── schema.sql                     # PostgreSQL 16 DDL for clients, instruments, orders, trades
│   ├── seed.py                        # Synthetic data generator (25k clients, 250k trades)
│   └── fixtures/
│       └── anomalies.json             # Anomaly definitions (August drop, Aug 14 spike, Expiry surge)
│
├── mcp_server/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── server.py                      # FastMCP server with SSE transport
│   ├── db.py                          # Read-only connection pool (statement_timeout = 2500ms)
│   └── tools/
│       ├── schema_tools.py            # inspect_schema, list_tables, get_metric_definition
│       └── query_tools.py             # execute_readonly_sql, explain_plan
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                        # FastAPI entrypoint + CORS + SSE endpoints
│   ├── config.py                      # Pydantic BaseSettings
│   │
│   ├── catalog/
│   │   ├── metrics.yaml               # Certified semantic metrics (Turnover, Yield, Fill Rate, RMS)
│   │   └── schema_metadata.json       # Table descriptions, business aliases, join paths
│   │
│   ├── graph/
│   │   ├── state.py                   # AgentState TypedDict definition
│   │   ├── workflow.py                # LangGraph StateGraph builder with cyclic self-correction
│   │   └── nodes/
│   │       ├── router.py              # Intent classifier (simple vs. diagnostic "Why" queries)
│   │       ├── retriever.py           # Hybrid vector/keyword retrieval over metrics & schema
│   │       ├── planner.py             # Multi-dimensional execution decomposition
│   │       ├── sql_generator.py       # Dialect-specific Postgres 16 SQL generator
│   │       ├── sql_validator.py       # sqlglot AST parsing & injection guardrails
│   │       ├── validator_node.py      # LangGraph AST inspection node
│   │       ├── executor.py            # MCP Client invoking execute_readonly_sql
│   │       ├── analytics.py           # Deterministic Pandas engine (PoP variance, contribution shares)
│   │       └── synthesizer.py         # Natural language summary + dynamic Recharts config
│   │
│   ├── services/
│   │   ├── mcp_client.py              # Unified MCP client (in-process + remote SSE)
│   │   └── semantic_search.py         # Hybrid catalog & schema retriever
│   │
│   └── api/
│       ├── schemas.py                 # Request/Response models & SSE event contracts
│       └── routes.py                  # POST /query, GET /stream, GET /metrics, GET /health
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx                    # Main Analytics Workspace
│   │   ├── types/agent.ts             # Event streams, ChartConfig, QueryTrace types
│   │   ├── hooks/useAgentStream.ts    # SSE reader for live LangGraph state updates
│   │   └── components/
│   │       ├── Header.tsx             # System branding & live status chips
│   │       ├── ChatInput.tsx          # Prompt bar with Angel One preset investigations
│   │       ├── ExecutionTrace.tsx     # Real-time state progress accordion with latency chips
│   │       ├── ChartRenderer.tsx      # Dynamic Recharts wrapper (Line, Bar, Area, KPI cards)
│   │       ├── SQLViewer.tsx          # AST-highlighted query inspector with retry badges
│   │       └── MetricsDrawer.tsx      # Slide-over semantic metric catalog viewer
│
├── evaluation/
│   ├── benchmark_data.json            # 60 golden queries across 5 tiers
│   ├── evaluate.py                    # Automated test runner calculating ESR, DFE, and Latency
│   ├── metrics.py                     # Quantitative metrics computation
│   └── benchmark_report.md            # Generated benchmark summary report
│
└── tests/
    ├── test_sql_validator.py          # AST validator unit tests
    ├── test_mcp_tools.py              # MCP server tools unit tests
    ├── test_agent_workflow.py         # LangGraph flagship integration tests
    └── test_self_correction.py        # Cyclic self-correction retry test
```

---

## 7. Quick Start Guide

### Option A: Zero-Config Local Development (Python + Vite)
InsightAgent features an automatic dual-engine architecture: it runs out-of-the-box on Windows/macOS/Linux without needing a local PostgreSQL or Docker setup.

```bash
# 1. Clone repository
git clone https://github.com/Prayash007/insight-agent.git
cd insight-agent

# 2. Setup Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r backend/requirements.txt

# 3. Seed capital markets database (25k clients, 250k trades)
python database/seed.py

# 4. Start Backend API (Port 8000)
python -m uvicorn backend.main:app --port 8000 --reload

# 5. Start Frontend Dashboard (Port 5173) in a second terminal
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** to access the live dashboard.

---

### Option B: Full Production Docker Deployment

```bash
# Spins up PostgreSQL 16, FastMCP SSE Server, FastAPI Backend, and React Nginx
docker-compose up --build -d
```

---

## 8. Running Automated Test Suites

```bash
# Run AST SQL Validator Unit Tests
python -m pytest tests/test_sql_validator.py -v

# Run MCP Tools Unit Tests
python -m pytest tests/test_mcp_tools.py -v

# Run LangGraph Workflow Flagship Integration Tests
python -m pytest tests/test_agent_workflow.py -v

# Run Cyclic Self-Correction Recovery Test
python -m pytest tests/test_self_correction.py -v

# Run Full 60-Query Golden Evaluation Benchmark
python evaluation/evaluate.py
```

---

## 9. Flagship Analytical Inquiries to Test

1. **"Why did F&O volume drop in August?"**
   - *Result:* Triggers `diagnostic_why` decomposition; isolates `OPTIDX` (-34.7% PoP delta) which contributed to 84.2% of the contraction; displays contribution breakdown bar chart and executive summary.
2. **"What caused the spike in RMS margin rejections on August 14?"**
   - *Result:* Identifies acute 14x surge (36.4% rejection rate on August 14 vs 2.8% baseline) caused by BankNifty peak margin snapshot breaches.
3. **"Compare Thursday expiry turnover against other weekdays"**
   - *Result:* Highlights 2.37x volume surges on Thursdays representing over 38% of total weekly retail option trading volume.
4. **"What is our order fill rate broken down by order type?"**
   - *Result:* Returns certified fill rates for MARKET, LIMIT, and SL orders.
5. **"Analyze net brokerage yield in bps by market segment"**
   - *Result:* Calculates Angel One flat-rate discount brokerage yields across F&O, Cash, and Commodities.
