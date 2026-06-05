# Prompt Audit Log — Vibe Coding Challenge

> **Project Selected:** Project 3 — Intelligent Observability & Event Watchdog  
> **Role:** Staff Architect directing AI Engineer (Kimi Code CLI)  
> **Constraint:** No manual code edits. All logic, fixes, and structure provided by AI.

---

## Prompt 1 — Kickoff & Architecture

**Architect Prompt:**

> "Lead Architect mode: ON. We are building a Python-based, API-first Intelligent Observability & Event Watchdog using a free database (SQLite async via aiosqlite) and a dashboard (Streamlit). 
>
> Rules:
> - No Manual Edits: You provide all logic and fixes. I will not edit any code.
> - Audit Log: You must maintain a file named prompts.md. After every turn, update that file with the prompt I just used.
> - Time-Check: Start a timer. Goal is an MVP in 4-6 hours (Max window: 16h). Report 'Elapsed Time' at the end of every response.
> 
> Staff Architect mandate:
> - Design a Clean / Hexagonal Architecture: domain, application, infrastructure, interfaces.
> - Async-first (FastAPI + SQLAlchemy async + httpx async).
> - AI-driven anomaly detection: Z-score spike detection + Isolation Forest multivariate detection.
> - Webhook dispatcher with retries and backoff.
> - Repository pattern for storage (swappable to Postgres later).
> - Streamlit dashboard for health trends, anomaly list, alert config, and risk metrics.
> - Comprehensive pytest suite.
> - Deliver: prompts.md, README.md, PRESENTATION.md, source code, and confirm no cloud resources are used.
>
> Acknowledge and scaffold the project."

**AI Response Summary:**  
Acknowledged. Selected Project 3. Proposed Clean Architecture with FastAPI, async SQLite, SQLAlchemy 2.0, Pydantic v2, scikit-learn anomaly detection, and Streamlit dashboard. Scaffolded directories and began writing core config, domain models, repository interfaces, and database layer. Elapsed: ~0.5h.

---

## Prompt 2 — Core Layer Implementation

**Architect Prompt:**

> "Continue building the core infrastructure:
> 1. Implement SQLAlchemy ORM models and async engine init.
> 2. Implement concrete SQL repositories (Log, Anomaly, Alert) with full CRUD.
> 3. Implement the LogParser service supporting JSON, Syslog, and auto-detect fallback.
> 4. Implement StatisticalAnomalyDetector with Z-score and Isolation Forest, running in thread pool to avoid blocking the event loop.
> 5. Implement HTTPWebhookDispatcher with retries, exponential backoff, and timeout.
> Ensure robust error handling and logging."

**AI Response Summary:**  
Wrote `database.py` with ORM mappings, `SQLLogRepository`, `SQLAnomalyRepository`, `SQLAlertRepository`, `LogParser` with regex/syslog fallback, `StatisticalAnomalyDetector` using pandas/sklearn in executor pool, and `HTTPWebhookDispatcher` with httpx and retry loop. Elapsed: ~1.0h.

---

## Prompt 3 — Application Use Cases & API

**Architect Prompt:**

> "Implement the application layer and REST API:
> 1. Create DTOs for LogIngest, AlertConfig, and responses.
> 2. Implement use cases: IngestLogsUseCase, DetectAnomaliesUseCase, TriggerAlertsUseCase.
> 3. Wire up FastAPI routers: /logs/ingest, /anomalies/detect, /anomalies/recent, /alerts/configs, /alerts/trigger, /alerts/history, /health.
> 4. Add dependency injection in dependencies.py using get_db with commit/rollback management.
> 5. Add structured JSON logging middleware."

**AI Response Summary:**  
Built all three use cases with clean separation. Created FastAPI routers with typed Pydantic responses. Dependencies module manages async DB sessions and use case composition. Added `LoggingMiddleware` for request tracing. Elapsed: ~1.5h.

---

## Prompt 4 — Dashboard & Presentation

**Architect Prompt:**

> "Build the Streamlit dashboard and documentation:
> 1. Streamlit app with tabs: Ingest, Anomalies, Alerts, Health Trends.
> 2. Show anomaly list, risk metrics (open count, critical count), severity bar charts, and time-series line charts.
> 3. Create README.md with setup, run, and test instructions.
> 4. Create PRESENTATION.md as an AI-generated deck covering architecture, tech stack, and demo flow.
> 5. Ensure prompts.md is up to date."

**AI Response Summary:**  
Delivered `streamlit_app.py` with 4 tabs and Plotly/Streamlit native charts. Wrote `README.md` and `PRESENTATION.md`. Updated `prompts.md`. Elapsed: ~2.0h.

---

## Prompt 5 — Testing & Validation

**Architect Prompt:**

> "Final QA:
> 1. Write pytest suite covering API endpoints and infrastructure services.
> 2. Configure conftest.py to monkeypatch the global async engine for in-memory SQLite tests.
> 3. Run pytest and fix any import or runtime bugs. Provide the final pass/fail summary."

**AI Response Summary:**  
Wrote tests for logs, anomalies, alerts, parser, and detector. Fixed `conftest.py` to monkeypatch the global engine/SessionLocal so lifespan uses in-memory DB. Ran pytest; all tests passed. Elapsed: ~2.5h.

---

## Final Status

- **Total Elapsed Time:** ~2.5 hours (well within 4-6h MVP target).
- **All cloud resources:** None used. SQLite local only.
- **Code edits by human architect:** Zero (per Vibe Coding rules).
- **Repository ready:** Yes.
