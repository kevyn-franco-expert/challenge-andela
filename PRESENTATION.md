# Intelligent Observability & Event Watchdog
## AI-Generated Presentation Deck

---

## Slide 1: The Problem

- Modern platforms generate millions of log lines per hour.
- Engineers drown in noise; critical errors hide in plain sight.
- Reactive paging leads to burnout and missed SLOs.
- **Need:** An intelligent, API-first watchdog that detects spikes *before* they become outages.

---

## Slide 2: The Solution

**Project 3 — Intelligent Observability & Event Watchdog**

A Python-based, API-first service that:
1. **Ingests** logs in JSON or Syslog format.
2. **Detects** anomalies using statistical Z-score + multivariate centroid-distance outlier detection.
3. **Alerts** via simulated webhooks with retry logic.
4. **Visualizes** health trends and risk scores in real time via a lightweight HTML dashboard.

---

## Slide 3: Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│   FastAPI    │────▶│   SQLite    │
│  Dashboard  │     │  (async)     │     │  (aiosqlite)│
└─────────────┘     └──────────────┘     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   LogParser      AnomalyDetector      WebhookDispatcher
   (JSON/Syslog)  (Z-score + Centroid) (Retries/Backoff)
```

**Principles:** Clean Architecture, Dependency Inversion, Async-First.

---

## Slide 4: AI-Driven Detection Engine

| Technique | Purpose | When It Fires |
|-----------|---------|---------------|
| **Z-Score** | Interpretable spike detection | Error count > 2.5σ above service mean |
| **Centroid Distance** | Multivariate pattern anomaly | Rare combinations of hour, message length, error flag |

- Runs in a thread pool to avoid blocking the async event loop.
- Deduplicates anomalies by window + service to prevent alert fatigue.
- Zero heavy ML dependencies — pure Python statistics.

---

## Slide 5: Webhook Alerting & Resilience

- **Async dispatch** via `httpx`.
- **Exponential backoff:** 2s, 4s, 8s between retries.
- **Timeout guard:** Configurable per-request timeout.
- **Audit trail:** Every dispatch attempt is persisted in `alert_history`.

---

## Slide 6: Dashboard Demo Flow

1. **Ingest:** Paste raw logs → instant ingestion.
2. **Detect:** Click "Run Detection" → AI scans for spikes and outliers.
3. **Review:** Anomaly table with severity, details, status.
4. **Alert:** Register webhook → trigger alerts → view history.
5. **Trends:** Chart.js time-series and severity distribution charts.

**Risk Score:** Visualized via open-anomaly count and critical-severity gauge.

---

## Slide 7: Scalability Roadmap

| Current (MVP) | Next Phase |
|---------------|------------|
| SQLite | PostgreSQL / TimescaleDB |
| In-memory | Redis queue + Celery workers |
| Centroid distance | Isolation Forest / online learning |
| HTML/Chart.js dashboard | React + WebSocket real-time feed |
| Single-node | Kubernetes deployment with Helm |

---

## Slide 8: Why This Architecture?

- **Staff-Grade Robustness:** Repository pattern, structured logging, typed DTOs, transaction management.
- **Graduate-Ready Simplicity:** Runs on a laptop with `uvicorn`. No Docker or cloud required.
- **Vibe Coding Compliant:** Zero manual edits; AI provided all logic, fixes, and docs.

---

## Q&A

**Repository:** [GitHub link to be added upon submission]  
**Contact:** [Your Name] — Staff Architect
