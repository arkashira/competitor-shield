## tech‑spec.md – Competitor‑Shield v1  

---  

### 1. Stack (language / framework / runtime)  

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend language** | **Python 3.11** | Rich AI/ML ecosystem (pandas, scikit‑learn, LangChain), fast prototyping, easy to embed LLM calls. |
| **Web framework** | **FastAPI** | Async‑first, OpenAPI auto‑generation, excellent for micro‑services, low overhead. |
| **LLM orchestration** | **LangChain + OpenAI / Anthropic APIs** | Unified prompt‑templating, tool‑calling, and caching. |
| **Task queue** | **Celery 5** + **Redis 7** | Background crawling, data enrichment, and model fine‑tuning. |
| **Database** | **PostgreSQL 15** (primary) + **TimescaleDB extension** for time‑series metrics | Strong relational model for entities, native JSONB for flexible competitor data, Timescale for trend analytics. |
| **Search / vector store** | **PGVector** (extension on PostgreSQL) | Leverages existing pgvector dataset, avoids separate vector DB, cheap on free‑tier cloud. |
| **Frontend** | **React 18** + **Vite** + **TypeScript** | Component‑driven UI, hot‑module reload, easy to ship as static assets to CDN. |
| **Styling** | **TailwindCSS** | Rapid UI iteration, minimal CSS bloat. |
| **Auth provider** | **Auth0 (Free tier)** – fallback to **Supabase Auth** for self‑hosted mode | Supports OIDC, social logins, MFA out‑of‑the‑box. |
| **Container runtime** | **Docker 26** (multi‑stage builds) | Consistent dev/prod parity, easy to deploy to any cloud. |
| **Infrastructure as Code** | **Terraform 1.7** + **Helm** (for k8s) | Declarative provisioning, reproducible environments. |

---  

### 2. Hosting (free‑tier‑first, specific platforms)  

| Component | Primary Free‑Tier Host | Secondary / Scale‑out |
|-----------|------------------------|-----------------------|
| **API & Workers** | **Render.com** (Free Web Service + Background Workers) – 750 hrs/mo, 1 GB RAM | **Fly.io** (Free 3 GB RAM, 160 GB‑hr) → Kubernetes on **DigitalOcean** (Droplets) when >10 k MAU |
| **PostgreSQL + PGVector** | **Supabase** (Free tier: 500 MB DB, 2 GB storage) – fits early‑stage prototype | **Neon.tech** (Serverless Postgres, free tier 20 M rows) → Managed RDS (AWS) for production |
| **Redis (Celery broker)** | **Upstash** (Free 10 MB) | **Redis Labs** (Free 30 MB) → Self‑hosted Redis on Fly.io for high‑throughput |
| **Static Frontend** | **Vercel** (Free – 100 GB bandwidth) | **Cloudflare Pages** (Free – 500 GB) |
| **CI/CD** | **GitHub Actions** (2 k free minutes/mo) | **GitHub Actions** + **Docker Hub** (Free tier) → **GitLab CI** if enterprise needed |
| **Domain & TLS** | **Cloudflare** (Free DNS + SSL) | Same – Cloudflare always free for DNS/TLS |

All services are provisioned via Terraform modules that default to the free tier; a single `terraform apply -var="env=prod"` swaps to paid resources.

---  

### 3. Data Model  

#### 3.1 Relational Tables (PostgreSQL)  

| Table | Key Fields | Important Columns | Indexes |
|-------|------------|-------------------|---------|
| **users** | `id (UUID PK)` | `email (unique)`, `name`, `auth_provider`, `created_at`, `last_login_at` | B‑tree on `email` |
| **organizations** | `id (UUID PK)` | `name`, `owner_user_id (FK→users.id)`, `plan (enum: free, pro)`, `created_at` | B‑tree on `owner_user_id` |
| **competitors** | `id (UUID PK)` | `org_id (FK→organizations.id)`, `name`, `website_url`, `category`, `source (enum: crawl, manual)`, `last_crawled_at`, `vector_id (FK→competitor_vectors.id)` | GIN on `category`, B‑tree on `org_id` |
| **competitor_snapshots** | `id (UUID PK)` | `competitor_id (FK)`, `snapshot_ts (timestamp)`, `features_jsonb`, `score_float` | B‑tree on `competitor_id`, BRIN on `snapshot_ts` |
| **insights** | `id (UUID PK)` | `org_id (FK)`, `title`, `description`, `generated_at`, `type (enum: SWOT, GAP, ROADMAP)`, `payload_jsonb` | GIN on `type` |
| **api_keys** | `key (text PK)`, `org_id (FK)`, `created_at`, `expires_at`, `scopes_jsonb` | B‑tree on `org_id` |
| **audit_log** | `id (bigserial PK)`, `org_id (FK)`, `user_id (FK)`, `action`, `resource_type`, `resource_id`, `timestamp`, `metadata_jsonb` | BRIN on `timestamp` |

#### 3.2 Vector Store (PGVector)  

| Table | Columns |
|-------|----------|
| **competitor_vectors** | `id (UUID PK)`, `embedding vector(1536)` (OpenAI text‑embedding‑ada‑002), `created_at` |
| **query_vectors** (optional) | `id (UUID PK)`, `org_id (FK)`, `embedding vector(1536)`, `created_at` |

*Embedding generation is performed in a Celery task after each crawl or manual upload.*

---  

### 4. API Surface (OpenAPI‑style)  

| Method | Path | Purpose | Auth / Scope |
|--------|------|---------|--------------|
| **POST** | `/api/v1/auth/login` | Exchange Auth0/Supabase token for internal JWT | Public |
| **GET** | `/api/v1/organizations/{org_id}` | Retrieve org profile & plan | JWT (org read) |
| **POST** | `/api/v1/competitors` | Register a new competitor (URL + optional manual data) | JWT (competitor write) |
| **GET** | `/api/v1/competitors/{competitor_id}` | Get latest snapshot & feature vector | JWT (competitor read) |
| **GET** | `/api/v1/competitors/{competitor_id}/history?since=ISO` | Time‑series of feature snapshots (for trend charts) | JWT (competitor read) |
| **POST** | `/api/v1/competitors/{competitor_id}/crawl` | Trigger immediate re‑crawl & re‑embedding (async) | JWT (competitor write) |
| **GET** | `/api/v1/insights?type=SWOT&limit=10` | Generate AI‑driven insight for the org (uses LLM) | JWT (insight read) |
| **POST** | `/api/v1/insights/{insight_id}/export` | Export insight as PDF/Markdown | JWT (insight read) |
| **GET** | `/api/v1/search?query=string&top_k=5` | Semantic search across all competitor vectors for the org | JWT (competitor read) |
| **POST** | `/api/v1/api-keys` | Create a scoped API key (for SaaS integrations) | JWT (admin) |
| **DELETE** | `/api/v1/api-keys/{key}` | Revoke API key | JWT (admin) |

*All endpoints return JSON; pagination via `cursor` token. Errors follow RFC 7807 problem‑details.*

---  

### 5. Security Model  

| Aspect | Implementation |
|--------|----------------|
| **Authentication** | JWT issued by Auth0 (or Supabase) → short‑lived (15 min) + refresh token (7 days). API keys are HMAC‑SHA256 signed strings stored hashed (bcrypt) in `api_keys`. |
| **Authorization (IAM)** | Role‑based: `owner`, `admin`, `member`. Scopes stored in `api_keys.scopes_jsonb` (e.g., `["competitor:read","insight:generate"]`). FastAPI dependency checks scopes per endpoint. |
| **Secret Management** | All external secrets (OpenAI API key, Redis password, DB credentials) stored in **HashiCorp Vault** (free dev mode) or **GitHub Actions Secrets** for CI. Runtime containers pull via Vault Agent sidecar. |
| **Transport Security** | Enforced TLS 1.3 via Cloudflare/Render front‑ends. Internal service‑to‑service calls use mTLS (generated by Vault). |
| **Data‑at‑Rest Encryption** | PostgreSQL Transparent Data Encryption (TDE) enabled on managed providers; backups encrypted with provider‑managed keys. |
| **Rate Limiting** | API Gateway (Render/Cloudflare Workers) – 100 req/min per JWT, 500 req/min per API key. |
| **Compliance** | GDPR‑ready: `users` table includes `consent_timestamp`; data export endpoint `/api/v1/users/me/data` (not yet in v1 but stubbed). |
| **Vulnerability Scanning** | Dependabot alerts + nightly Trivy scan in CI pipeline. |

---  

### 6. Observability  

| Layer | Tool | What is Collected |
|-------|------|-------------------|
| **Logs** | **Grafana Loki** (via Docker driver) + **Fluent Bit** | Structured JSON logs: request_id, user_id, endpoint, latency, error stack. |
| **Metrics** | **Prometheus** (scraped from FastAPI `/metrics`) + **Grafana Cloud (free tier)** | HTTP latency (p95), request rates, Celery task queue depth, DB connection pool usage, Redis hit‑rate. |
| **Traces** | **OpenTelemetry** SDK (Python) → **Jaeger** (hosted on Fly.io) | End‑to‑end request trace across API → DB → LLM call → vector search. |
| **Alerting** | **Grafana Alerting** → Slack webhook + email for >5 min high error rate, DB CPU >80%, vector search latency >300 ms. |
| **Health Checks** | `/healthz` (FastAPI) returns DB, Redis, LLM API ping status; `/readyz` for k8s readiness. |
| **Dashboards** | Pre‑built Grafana dashboards for: API performance, competitor crawl success/failure, insight generation cost (LLM token usage). |

---  

### 7. Build / CI  

| Stage | Tool | Steps |
|-------|------|-------|
| **Code Checkout** | GitHub Actions | `actions/checkout@v4` |
| **Static Analysis** | `ruff` (lint) + `mypy` (type check) | Fail on warnings. |
| **Unit Tests** | `pytest` + `pytest‑asyncio` | Coverage ≥ 85 %; upload to **Codecov** (free). |
| **Integration Tests** | Docker‑compose spin‑up of Postgres, Redis, FastAPI container; run subset of tests against real services. |
| **Security Scan** | **Trivy** (container) + **Dependabot** | Fail on CVE > 7. |
| **Build Image** | `docker buildx` multi‑stage → `ghcr.io/axentx/competitor-shield:${{ github.sha }}` | Tag `latest` on `main`. |
| **Push** | GitHub Container Registry (private) | |
| **Deploy** | **Render Deploy Hook** (via GitHub Action) or **Fly.io** `flyctl deploy` for prod. |
| **Post‑Deploy Smoke Test** | `curl` health endpoints, verify DB migration via Alembic. |
| **Rollback** | Render/Fly rollback to previous image tag via GitHub Action on failure. |

*All secrets injected via GitHub Actions encrypted variables; Terraform plan/apply runs in a separate CI job with a Vault token.*  

---  

**End of tech‑spec.md**.