"""API REST local para el modelo TechMind."""

from __future__ import annotations

import os
import sys

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


PACKAGE_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PACKAGE_ROOT)
    )


from techmind import TechMindPredictor

from .schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
    RootResponse
)


API_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="milliseconds"
    )


def _resolve_package_root() -> Path:
    configured_root = os.getenv(
        "TECHMIND_PACKAGE_ROOT"
    )

    if configured_root:
        return Path(
            configured_root
        ).expanduser().resolve()

    return PACKAGE_ROOT


@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    package_root = (
        _resolve_package_root()
    )

    predictor = TechMindPredictor(
        package_root=package_root,
        verify_hash=True
    )

    app.state.predictor = predictor
    app.state.started_at_utc = _utc_now()
    app.state.package_root = package_root

    yield

    app.state.predictor = None


app = FastAPI(
    title="TechMind Classification API",
    description=(
        "API local para clasificar contenido tecnológico "
        "en backend, cloud, datascience y frontend."
    ),
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# No se habilitan orígenes externos por defecto.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)


def _get_predictor(
    request: Request
) -> TechMindPredictor:
    predictor = getattr(
        request.app.state,
        "predictor",
        None
    )

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "El modelo todavía no está disponible."
            )
        )

    return predictor


@app.get(
    "/",
    response_model=RootResponse,
    tags=["General"]
)
def root() -> dict[str, Any]:
    return {
        "name": "TechMind Classification API",
        "version": API_VERSION,
        "status": "available",
        "endpoints": {
            "health": "/health",
            "model_info": "/model-info",
            "predict": "/predict",
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Monitoring"]
)
def health(
    request: Request
) -> dict[str, Any]:
    predictor = _get_predictor(
        request
    )

    model_health = (
        predictor.health()
    )

    return {
        "status": "ok",
        "ready": True,
        "api_version": API_VERSION,
        "model_name": model_health.get(
            "model_name"
        ),
        "model_status": model_health.get(
            "model_status"
        ),
        "model_sha256": model_health[
            "model_sha256"
        ],
        "classes": model_health[
            "classes"
        ],
        "tfidf_features": model_health[
            "tfidf_features"
        ],
        "word_features": model_health.get(
            "word_features"
        ),
        "char_features": model_health.get(
            "char_features"
        ),
        "total_features": model_health.get(
            "total_features"
        ),
        "word_features": model_health.get(
            "word_features"
        ),
        "char_features": model_health.get(
            "char_features"
        ),
        "total_features": model_health.get(
            "total_features"
        ),
        "pipeline_steps": model_health[
            "pipeline_steps"
        ],
        "started_at_utc": (
            request.app.state
            .started_at_utc
        ),
        "checked_at_utc": _utc_now()
    }


@app.get(
    "/model-info",
    response_model=ModelInfoResponse,
    tags=["Model"]
)
def model_info(
    request: Request
) -> dict[str, Any]:
    predictor = _get_predictor(
        request
    )

    model_health = (
        predictor.health()
    )

    return {
        "api_version": API_VERSION,
        "model_name": model_health.get(
            "model_name"
        ),
        "model_status": model_health.get(
            "model_status"
        ),
        "model_version": (
            model_health.get(
                "model_version"
            )
            or predictor.config.get(
                "model_version"
            )
            or predictor.config.get(
                "version_modelo"
            )
        ),
        "model_sha256": model_health[
            "model_sha256"
        ],
        "classes": model_health[
            "classes"
        ],
        "tfidf_features": model_health[
            "tfidf_features"
        ],
        "word_features": model_health.get(
            "word_features"
        ),
        "char_features": model_health.get(
            "char_features"
        ),
        "total_features": model_health.get(
            "total_features"
        ),
        "pipeline_steps": model_health[
            "pipeline_steps"
        ],
        "limits": (
            predictor.config.get(
                "limits"
            )
            or predictor.config.get(
                "limites_entrada",
                {}
            )
        ),
        "margin_thresholds": (
            predictor.config.get(
                "margin_thresholds"
            )
            or predictor.config.get(
                "umbrales_margen_descriptivos",
                {}
            )
        ),
        "margin_is_probability": False,
        "optional_explanations": True,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"]
)
def predict(
    payload: PredictionRequest,
    request: Request
) -> dict[str, Any]:
    predictor = _get_predictor(
        request
    )

    try:
        return predictor.predict(
            texts=payload.textos,
            include_explanation=(
                payload.incluir_explicacion
            ),
            explanation_top_n=(
                payload.top_n_explicacion
            ),
            top_k=payload.top_k
        )

    except (
        TypeError,
        ValueError
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "El modelo no pudo completar "
                "la inferencia."
            )
        ) from error
