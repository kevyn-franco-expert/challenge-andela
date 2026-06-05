# Intelligent Observability & Event Watchdog

> **Project 3 — Graduate Vibe Coding Challenge**  
> Python-based, API-first observability platform with AI-driven anomaly detection, webhook alerting, and a real-time dashboard.

## Architecture

```
┌──────────────┐      ┌─────────────────┐      ┌──────────────────┐
│   Browser    │──────▶   FastAPI       │──────▶  SQLite (async)  │
│  Dashboard   │      │   REST API      │      │   aiosqlite      │
└──────────────┘      └─────────────────┘      └──────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  Clean Architecture Layers     │
              │  • Domain (Models, Interfaces) │
              │  • Application (Use Cases)     │
              │  • Infrastructure (DB, ML)     │
              │  • Interfaces (API, Dashboard) │
              └──────────────────────────────┘
```

## Tech Stack

- **Runtime:** Python 3.9+
- **API:** FastAPI + Uvicorn (async)
- **Database:** SQLite via `aiosqlite` (free tier, swappable to Postgres)
- **ORM:** SQLAlchemy 2.0 (async)
- **ML/Stats:** Pure Python statistics (Z-score + centroid-distance multivariate outlier detection)
- **HTTP Client:** httpx (async webhook dispatch)
- **Dashboard:** Vanilla HTML/CSS/JS with Chart.js (served by FastAPI)
- **Testing:** pytest, pytest-asyncio, httpx

## Quick Start

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/dashboard`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/logs/ingest` | Ingest raw log lines (JSON / Syslog / auto) |
| POST | `/anomalies/detect` | Run AI anomaly detection on recent logs |
| GET | `/anomalies/recent` | List recent anomalies |
| POST | `/alerts/configs` | Register a webhook alert endpoint |
| GET | `/alerts/configs` | List registered alert configs |
| POST | `/alerts/trigger` | Manually trigger alert dispatch for open anomalies |
| GET | `/alerts/history` | View alert dispatch history |
| GET | `/health` | Health check |
| GET | `/dashboard` | Real-time HTML dashboard |

## Testing

```bash
pytest -v
```

Tests use an in-memory SQLite database via monkeypatched engine/SessionLocal.

## Design Decisions

- **Clean Architecture:** Domain layer has zero dependencies. Repositories and services are pluggable.
- **Async-First:** All I/O (DB, HTTP) is async to support high-throughput ingestion.
- **AI Detection:** Hybrid approach — Z-score for interpretable error spikes, centroid-distance for multivariate pattern anomalies. No heavy ML libraries required.
- **Webhook Resilience:** Exponential backoff retries, timeout handling, and structured error logging.
- **Scalability Path:** Swap SQLite → PostgreSQL by changing `DATABASE_URL`. Swap in-memory queue → Redis by adding a Celery/Redis task broker.

## Professional Responsibility

- **No cloud resources** were provisioned for this MVP. SQLite runs locally.
- All accounts and environments are local-only.
