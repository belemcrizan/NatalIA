# syntax=docker/dockerfile:1
FROM python:3.12-slim AS frontend
ENV NODE_VERSION=22.14.0
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl xz-utils \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
        | tar -xJ -C /usr/local --strip-components=1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npm run build && test -f /build/natalia/web/index.html

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 NATALIA_DB_PATH=/data/natalia.db
WORKDIR /app
COPY requirements.lock ./
RUN pip install -r requirements.lock && useradd --uid 10001 --create-home natalia && mkdir /data && chown natalia:natalia /data
COPY pyproject.toml ./
COPY natalia ./natalia
COPY --from=frontend /build/natalia/web ./natalia/web
RUN test -f natalia/web/index.html && pip install --no-deps .
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=45s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=2)"
CMD ["uvicorn", "natalia.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
