# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

# --------------------------------------------------------
# METADATA
# --------------------------------------------------------
LABEL org.opencontainers.image.title="TechMind"
LABEL org.opencontainers.image.version="1.2.0-multilingual"
LABEL techmind.model.status="validated_experimental_candidate"
LABEL techmind.model.sha256="1a495520f642416e7dd391f97417cd3d12dcd82ab11636b7f190e5ed6dafea61"

# --------------------------------------------------------
# PYTHON
# --------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# --------------------------------------------------------
# SYSTEM DEPENDENCIES
# --------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# PYTHON DEPENDENCIES
# --------------------------------------------------------
COPY deploy/v1.2.0-multilingual/requirements-v1.2.txt \
     /tmp/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && grep -v '^torch==' /tmp/requirements.txt > /tmp/requirements-no-torch.txt \
    && python -m pip install "torch==2.13.0+cpu" --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r /tmp/requirements-no-torch.txt \
    && python -m pip check \
    && python -c "import torch; assert torch.__version__.startswith('2.13.0'); assert not torch.cuda.is_available(); print('TORCH_CPU_OK', torch.__version__)"

# --------------------------------------------------------
# APPLICATION
# --------------------------------------------------------
COPY techmind_v12 /app/techmind_v12
COPY techmind_api_v12 /app/techmind_api_v12

# --------------------------------------------------------
# FROZEN MODEL ARTIFACT
# --------------------------------------------------------
COPY models/experimental/v1.2.0-multilingual/techmind_hybrid_v1_2_0_multilingual.joblib \
     /app/models/experimental/v1.2.0-multilingual/techmind_hybrid_v1_2_0_multilingual.joblib

# Verify exact validated artifact.
RUN echo "1a495520f642416e7dd391f97417cd3d12dcd82ab11636b7f190e5ed6dafea61  /app/models/experimental/v1.2.0-multilingual/techmind_hybrid_v1_2_0_multilingual.joblib" \
    | sha256sum -c -

# --------------------------------------------------------
# NON-ROOT USER
# --------------------------------------------------------
RUN groupadd --gid 10001 techmind \
    && useradd \
       --uid 10001 \
       --gid 10001 \
       --create-home \
       --shell /usr/sbin/nologin \
       techmind \
    && mkdir -p /home/techmind/.cache/huggingface \
    && chown -R techmind:techmind /home/techmind /app

ENV HF_HOME=/home/techmind/.cache/huggingface

USER techmind

# --------------------------------------------------------
# DOWNLOAD AND BAKE MINILM INTO IMAGE
# --------------------------------------------------------
RUN python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'); assert m.get_sentence_embedding_dimension()==384; print('MINILM_BUILD_OK')"

# --------------------------------------------------------
# OFFLINE RUNTIME
# --------------------------------------------------------
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV TOKENIZERS_PARALLELISM=false

ENV TECHMIND_V12_MODEL_PATH=/app/models/experimental/v1.2.0-multilingual/techmind_hybrid_v1_2_0_multilingual.joblib

# --------------------------------------------------------
# API
# --------------------------------------------------------
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import json,urllib.request; d=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3)); assert d['status']=='ok' and d['model_loaded'] is True" || exit 1

# --------------------------------------------------------
# UVICORN
# --------------------------------------------------------
CMD ["python", "-m", "uvicorn", "techmind_api_v12.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
