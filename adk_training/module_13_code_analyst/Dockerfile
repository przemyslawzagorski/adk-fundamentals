# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Narzedzia systemowe potrzebne dla git/build tooli
RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# --- Build stage: instalacja zaleznosci ---
FROM base AS deps
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Runtime ---
FROM base AS runtime
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY --chown=app:app . /app/

ENV CODE_ANALYST_HOST=0.0.0.0 \
    CODE_ANALYST_PORT=8088 \
    CODE_ANALYST_DATA=/data \
    CODE_ANALYST_LOG_JSON=1 \
    CODE_ANALYST_RELOAD=0

RUN mkdir -p /data && chown app:app /data
VOLUME ["/data"]
USER app
EXPOSE 8088

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8088/health || exit 1

WORKDIR /app/web
CMD ["python", "app.py"]
