# TECH_SPEC.md – Competitor Shield

**Document version:** 1.0.0  
**Last updated:** 2026‑06‑25  
**Author:** Senior Product/Engineering Lead – AxentX  

---  

## 1. Overview  

Competitor Shield is an AI‑driven alert system that ingests competitive‑threat signals, enriches them with contextual insights, and notifies stakeholders in real‑time. The service is built as a **modular, cloud‑native microservice** exposing a clean REST API (FastAPI) and a Python SDK (`AlertSystem` class).  

Key goals:

| Goal | Success Metric |
|------|----------------|
| **Real‑time detection** | ≤ 2 s latency from threat ingestion to notification |
| **Actionable insights** | ≥ 80 % of generated insights rated “useful” in user surveys |
| **Scalability** | Horizontal scaling to 10 k TPS with < 200 ms 99‑pct latency |
| **Reliability** | 99.9 % uptime SLA (four‑nines) |
| **Security & compliance** | Data encrypted at rest & in‑flight, GDPR‑ready, role‑based access control (RBAC) |

---  

## 2. Architecture Overview  

```
+-------------------+          +-------------------+          +-------------------+
|   External APIs   |  HTTPS   |   API Gateway     |  gRPC/   |   Insight Engine  |
| (Webhooks, SDK)   | <------> | (FastAPI + Auth) |  HTTP    | (vLLM / SGLang)   |
+-------------------+          +-------------------+          +-------------------+
          |                               |                               |
          |                               |                               |
          v                               v                               v
+-------------------+          +-------------------+          +-------------------+
|   Threat Service  |  Async   |   Notification    |  Async   |   Persistence     |
| (Celery Workers)  | <------> |   Service         | <------> | (PostgreSQL)      |
+-------------------+          +-------------------+          +-------------------+
          ^                               ^                               ^
          |                               |                               |
          |                               |                               |
+-------------------+          +-------------------+          +-------------------+
|   Ingestion Layer |  Kafka   |   Queue (Redis)   |  Redis   |   Metrics / Logs  |
| (REST / Kafka)    | <------> |   (Celery Beat)   | <------> |   (Prometheus)   |
+-------------------+          +-------------------+          +-------------------+
```

* **API Gateway** – FastAPI app with JWT‑based auth, request validation (Pydantic), rate‑limiting, and OpenAPI docs.  
* **Ingestion Layer** – Accepts threat payloads via REST (`/threats`) or Kafka topic (`threats.raw`). Normalises data and pushes to the **Threat Service** queue.  
* **Threat Service** – Celery workers that persist threats, compute severity, and trigger the **Insight Engine**.  
* **Insight Engine** – Stateless LLM inference service (vLLM or SGLang) that generates contextual insights, risk scores, and recommended actions.  
* **Notification Service** – Sends emails, Slack messages, or push notifications using async workers (SMTP, Slack API, Firebase).  
* **Persistence** – PostgreSQL (SQLAlchemy ORM) stores threats, users, subscriptions, and audit logs.  
* **Observability** – Prometheus + Grafana for metrics, Loki for logs, OpenTelemetry for tracing.  

---  

## 3. Core Components  

| Component | Responsibility | Implementation Details |
|-----------|----------------|------------------------|
| **AlertSystem SDK** | Python wrapper for the REST API (instantiation, threat CRUD, notification, insights). | `alert_system/__init__.py` – thin client using `httpx.AsyncClient`. |
| **API Service** | Exposes `/threats`, `/users`, `/insights`, `/notifications`. | FastAPI v0.110, Pydantic v2, `uvicorn[standard]`. |
| **Threat Processor** | Validates, enriches, persists threats; triggers insight generation. | Celery 5.4, Redis broker, PostgreSQL backend. |
| **Insight Engine** | Generates AI‑driven analysis per threat. | vLLM 0.4 (GPU‑accelerated), optional SGLang for structured generation. |
| **Notification Engine** | Delivers alerts via configurable channels. | Celery workers, `aiosmtplib`, `slack_sdk`, `firebase-admin`. |
| **Scheduler** | Periodic health‑checks, digest email generation. | Celery Beat, cron‑style schedules. |
| **Data Store** | Relational storage for core entities. | PostgreSQL 15, SQLAlchemy 2.0, Alembic migrations. |
| **Cache / Queue** | Fast transient storage for task payloads. | Redis 7 (both broker & cache). |
| **Observability Stack** | Metrics, logs, tracing. | Prometheus, Grafana, Loki, OpenTelemetry SDK. |

---  

## 4. Data Model  

### 4.1 Entity Diagram  

```
User
 └─> Subscription (many‑to‑many between
