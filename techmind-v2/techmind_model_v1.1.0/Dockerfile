FROM python:3.11-slim

ARG APP_UID=10001
ARG APP_GID=10001

LABEL org.opencontainers.image.title="TechMind Classification API"
LABEL org.opencontainers.image.description="API REST para clasificación de contenido tecnológico"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2026-08-05T19:51:45"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TECHMIND_PACKAGE_ROOT=/app \
    TECHMIND_API_HOST=0.0.0.0 \
    TECHMIND_API_PORT=8000

WORKDIR /app

RUN groupadd \
        --gid "${APP_GID}" \
        techmind \
    && useradd \
        --uid "${APP_UID}" \
        --gid "${APP_GID}" \
        --create-home \
        --shell /usr/sbin/nologin \
        techmind

COPY requirements.txt requirements-api.txt ./

RUN python -m pip install \
        --no-cache-dir \
        -r requirements-api.txt

COPY --chown=techmind:techmind techmind ./techmind
COPY --chown=techmind:techmind techmind_api ./techmind_api
COPY --chown=techmind:techmind artifacts ./artifacts
COPY --chown=techmind:techmind deployment ./deployment

COPY --chown=techmind:techmind \
    VERSION \
    package_metadata.json \
    runtime.json \
    ./

USER techmind

EXPOSE 8000

HEALTHCHECK \
    --interval=30s \
    --timeout=6s \
    --start-period=20s \
    --retries=3 \
    CMD ["python", "deployment/healthcheck.py"]

CMD [
    "python",
    "-m",
    "uvicorn",
    "techmind_api.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
    "--workers",
    "1"
]
