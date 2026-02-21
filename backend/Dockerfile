# ── Backend Dockerfile ────────────────────────────────────────────────────────
# Multi-stage build: small final image with only runtime dependencies.
# Stage 1 installs build tools; Stage 2 copies only the venv.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS builder

WORKDIR /build

# System deps for asyncpg (libpq) and building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ── Runtime stage ────────────────────────────────────────────────────────────

FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --system --no-create-home appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONPATH=/app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
