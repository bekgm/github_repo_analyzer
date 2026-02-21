# GitHub Repository Analyzer

A production-ready full-stack application that analyzes any public GitHub repository, providing deep code metrics, contributor analytics, and AI-powered insights via Google Gemini.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│  FastAPI API  │────▶│  PostgreSQL  │
│  (Vite/TS)  │     │              │     │             │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐     ┌─────────────┐
                    │ Celery Worker │────▶│    Redis   │
                    │              │     │ Cache+Broker │
                    └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐     ┌─────────────┐
                    │ GitHub API   │     │ Gemini AI    │
                    └──────────────┘     └─────────────┘
```

### Clean Architecture Layers

| Layer | Directory | Responsibility |
|---|---|---|
| **Domain** | `app/domain/` | Entities, repository interfaces, pure business logic |
| **Use Cases** | `app/usecases/` | Application orchestration (no framework deps) |
| **Infrastructure** | `app/infrastructure/` | DB, Redis, GitHub client, Celery tasks |
| **API** | `app/api/` | FastAPI routes, schemas, middleware |

**Dependency rule**: outer layers depend inward. Domain depends on nothing.

## Features

### Code Metrics
- Total commits, average commit size
- Commits per day / month
- Code churn (additions/deletions)
- Average time between commits
- Bus factor calculation
- Top contributors ranking
- Language distribution

### Visualizations (React Frontend)
- Language pie chart (Recharts)
- Commit frequency bar chart
- Contributor ranking with progress bars
- Metrics dashboard cards

### AI Analysis (Gemini)
- Project summary generation
- README quality scoring (0-10)
- Tech stack detection
- Architecture analysis

## Quick Start

### Prerequisites
- Docker & Docker Compose
- GitHub personal access token (optional, increases rate limit)
- Gemini API key (optional, enables AI features)

### 1. Clone & Configure

```bash
cd backend
cp .env
# Edit .env with your API keys
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

Services:
- **API**: http://localhost:8000
- **Swagger docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Analyze a Repository

```bash
curl -X POST http://localhost:8000/api/v1/analyses/analyze \
  -H "Content-Type: application/json" \
  -d '{"owner": "fastapi", "name": "fastapi"}'
```

Response:
```json
{
  "analysis_id": "uuid-here",
  "repository_id": "uuid-here",
  "status": "pending",
  "message": "Analysis queued. Poll GET /analyses/{analysis_id} for results."
}
```

Then poll for results:
```bash
curl http://localhost:8000/api/v1/analyses/{analysis_id}
```

## Project Structure

```
backend/
├── app/
│   ├── api/                    # FastAPI layer
│   │   ├── routes/
│   │   │   ├── analysis.py     # POST /analyze, GET /analyses/{id}
│   │   │   └── health.py       # GET /health
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── dependencies.py     # DI composition root
│   │   └── rate_limit.py       # slowapi rate limiter
│   ├── core/                   # Config, logging, exceptions
│   │   ├── config.py           # pydantic-settings
│   │   ├── logging.py          # structlog (JSON in prod)
│   │   └── exceptions.py       # Exception hierarchy
│   ├── domain/                 # Pure business logic
│   │   ├── entities.py         # User, Repository, Analysis, etc.
│   │   ├── repositories.py     # Abstract repository interfaces
│   │   └── services.py         # Bus factor, churn, aggregation
│   ├── infrastructure/         # External concerns
│   │   ├── cache/
│   │   │   └── redis_cache.py  # Redis cache + CachedGitHubClient
│   │   ├── database/
│   │   │   ├── models.py       # SQLAlchemy ORM models
│   │   │   ├── session.py      # Async engine & session
│   │   │   └── repositories.py # Concrete repo implementations
│   │   ├── external/
│   │   │   ├── github_client.py # GitHub REST API client
│   │   │   └── gemini_client.py # Gemini AI client
│   │   └── jobs/
│   │       ├── celery_app.py   # Celery instance config
│   │       └── celery_tasks.py # Background analysis task
│   ├── usecases/               # Application services
│   │   ├── analyze_repository.py
│   │   └── get_analysis.py
│   └── main.py                 # FastAPI app factory
├── alembic/                    # Database migrations
├── tests/
│   ├── unit/                   # Pure logic tests (fast)
│   └── integration/            # API tests (needs DB)
├── Dockerfile
├── pyproject.toml
└── alembic.ini

frontend/
├── src/
│   ├── api/client.ts           # Axios API client + types
│   ├── components/
│   │   ├── MetricsGrid.tsx
│   │   ├── LanguagePieChart.tsx
│   │   ├── CommitFrequencyChart.tsx
│   │   ├── ContributorRanking.tsx
│   │   └── AIInsightsPanel.tsx
│   └── pages/
│       ├── HomePage.tsx        # Search form
│       └── AnalysisPage.tsx    # Results dashboard
├── Dockerfile
└── package.json
```

## Database Schema

```
users ──────────────┐
                    │
repositories ───────┤
  │                 │
  ▼                 │
analyses ◄──────────┘
  │
  ├──▶ commits_stats
  └──▶ contributors
```

Key design:
- **UUIDs** everywhere — safe for distributed worker ID generation
- **CASCADE deletes** from repository → analyses → stats
- **Indexes** on foreign keys, status, full_name
- **JSON columns** for language_distribution and detected_tech_stack

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/analyses/analyze` | Trigger analysis (returns 202) |
| `GET` | `/api/v1/analyses/{id}` | Get analysis detail |
| `GET` | `/api/v1/analyses/?repository_id=` | List analyses (paginated) |
| `GET` | `/api/v1/health` | Health check |

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub PAT for higher rate limits | _(empty)_ |
| `GEMINI_API_KEY` | Google Gemini API key | _(empty)_ |
| `POSTGRES_*` | Database connection | localhost:5432 |
| `REDIS_URL` | Redis for cache | redis://localhost:6379/0 |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per IP | 30 |

## Running Tests

```bash
# Unit tests (no external deps needed)
cd backend
pytest tests/unit -v

# Full suite (needs Postgres + Redis)
pytest tests/ -v --cov=app
```

## Key Architectural Decisions

1. **Clean Architecture** — domain logic is isolated from frameworks; you could swap FastAPI for Flask or SQLAlchemy for another ORM without touching business rules.

2. **Celery for background jobs** — GitHub API pagination + Gemini AI calls take 30-120s. Celery with `acks_late=True` ensures work isn't lost if a worker crashes.

3. **Redis dual-use** — cache layer (GitHub responses) and Celery broker share Redis but use different DB numbers (0, 1, 2) for isolation.

4. **CachedGitHubClient (Proxy Pattern)** — transparently wraps the raw client; callers don't know caching exists. Immutable data (commit details) cached 24h; mutable data (repo metadata) cached 1h.

5. **Bus Factor algorithm** — sorts contributors by commits descending, accumulates until ≥80% threshold. A bus factor of 1 is a red flag.

6. **Async everything in FastAPI** — `asyncpg` + `httpx` + `redis.asyncio` keep the event loop free. Celery tasks use `asyncio.run()` as a bridge.

7. **Rate limiting** — `slowapi` with Redis backend, per-IP sliding window. The `/analyze` endpoint has a tighter 10/min limit.

## License

MIT
