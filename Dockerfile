FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 NATALIA_DB_PATH=/data/natalia.db
WORKDIR /app
COPY requirements.lock ./
RUN pip install -r requirements.lock && useradd --uid 10001 --create-home natalia && mkdir /data && chown natalia:natalia /data
COPY pyproject.toml ./
COPY natalia ./natalia
RUN test -f natalia/web/index.html && pip install --no-deps .
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=15s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=2)"
CMD ["uvicorn", "natalia.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
