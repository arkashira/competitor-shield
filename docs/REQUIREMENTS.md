# REQUIREMENTS.md  

**Project:** competitor‑shield  
**Owner:** Axentx – AI‑Workforce Team  
**Version:** 1.0.0  
**Date:** 2026‑06‑25  

---  

## 1. Introduction  

Competitor Shield is an AI‑driven alert system that continuously monitors external data sources (news feeds, social media, patents, product releases, job postings, etc.) for signals indicating competitive threats. When a threat is detected, the system enriches the signal with contextual analysis, generates actionable insights, and notifies the appropriate stakeholders.  

The purpose of this document is to capture **all** product requirements that must be satisfied for the first production‑ready release (MVP). Requirements are written to be **clear, testable, and shippable** without overlapping existing Axentx products (e.g., iceoryx2 IPC library).  

---  

## 2. Scope  

| In‑Scope | Out‑Of‑Scope |
|----------|--------------|
| • Real‑time ingestion of configurable data sources (RSS, Twitter API, public RSS, custom webhook).<br>• Threat representation, storage, and retrieval via the `AlertSystem` class.<br>• AI‑powered enrichment (entity extraction, sentiment, similarity to known threat patterns).<br>• Multi‑channel user notification (email, Slack, webhook).<br>• Insight generation (risk score, recommended actions, impact estimate).<br>• RESTful API and Python SDK exposing the core methods (`add_threat`, `get_threats`, `notify_users`, `provide_insights`). | • Full‑blown SIEM integration.<br>• On‑premise deployment (MVP is SaaS‑only).<br>• Deep‑learning model training pipelines (pre‑trained models are used).<br>• Legal/compliance audit trails beyond basic GDPR compliance. |

---  

## 3. Definitions  

| Term | Meaning |
|------|---------|
| **Threat** | A discrete event or signal that may indicate a competitor’s strategic move (e.g., product launch, hiring spree, patent filing). |
| **Insight** | Structured recommendation derived from AI analysis (risk score, mitigation steps). |
| **Stakeholder** | End‑user who receives alerts (product manager, security analyst, executive). |
| **AlertSystem** | Primary Python class that encapsulates ingestion, storage, analysis, and notification logic. |
| **SLA** | Service‑Level Agreement for availability and latency (see NFR‑1). |

---  

## 4. Functional Requirements  

| ID | Requirement | Description | Acceptance Test |
|----|-------------|-------------|-----------------|
| **FR‑1** | **Threat Ingestion** | The system must ingest threat signals from at least three configurable sources (RSS, Twitter API, custom webhook). Each source can be enabled/disabled at runtime via a JSON config file. | Inject 10 mock signals via each source; `AlertSystem.add_threat` stores 30 records. |
| **FR‑2** | **Threat Persistence** | All ingested threats must be persisted in a PostgreSQL database with ACID guarantees. The schema must include `id`, `source`, `raw_payload`, `timestamp`, `status`. | After ingestion, a SQL query returns the exact number of stored rows with correct fields. |
| **FR‑3** | **AI Enrichment** | Upon insertion, each threat is automatically processed by a pre‑trained transformer model (e.g., `distilbert-base-uncased`) to extract: <br>• Named entities (companies, products) <br>• Sentiment (positive/negative/neutral) <br>• Similarity to known threat patterns (cosine similarity > 0.75 triggers “high‑confidence”). | For a known threat payload, the system returns the expected entities, sentiment, and similarity flag. |
| **FR‑4** | **Risk Scoring** | The system must compute a numeric risk score (0‑100) based on AI outputs, source credibility, and configurable weightings. The score is stored with the threat record. | Provide a threat with known attributes; verify the computed score matches the formula in the spec. |
| **FR‑5** | **Insight Generation** | `AlertSystem.provide_insights(threat_id)` returns a JSON object containing: <br>• `risk_score` <br>• `summary` (max 200 chars) <br>• `recommended_actions` (list of up to 5 items) <br>• `impact_estimate` (low/medium/high). | Call the method on a seeded threat; validate JSON schema and content. |
| **FR‑6** | **User Notification** | `AlertSystem.notify_users(threat_id)` must dispatch the insight to all stakeholders defined in a `recipients.yaml` file via the enabled channels (email via SMTP, Slack webhook, generic HTTP webhook). Delivery must be attempted at least three times with exponential back‑off. | Simulate a failure on the first attempt; verify two retries occur and the final delivery succeeds. |
| **FR‑7** | **Threat Retrieval API** | Expose a REST endpoint `GET /threats` supporting pagination, filtering by `source`, `status`, `risk_score` range, and date range. | Issue a request with filters; response contains only matching threats and correct pagination metadata. |
| **FR‑8** | **SDK Wrapper** | Provide a Python SDK (`competitor_shield.sdk`) that wraps the REST API and offers the same class‑based interface (`AlertSystem`). The SDK must be installable via `pip`. | `pip install competitor_shield` succeeds; sample script using SDK can add a threat and retrieve insights. |
| **FR‑9
