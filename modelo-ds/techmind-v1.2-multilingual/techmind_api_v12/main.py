\
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
import os

from fastapi import (
    FastAPI,
    HTTPException,
)

from techmind_v12 import (
    TechMindPredictor,
)

from .schemas import (
    PredictRequest,
    PredictResponse,
)


API_VERSION = "1.2.0"

MODEL_VERSION = (
    "1.2.0-multilingual"
)


def _resolve_root() -> Path:

    return (
        Path(__file__)
        .resolve()
        .parents[1]
    )


ROOT = _resolve_root()


DEFAULT_MODEL_PATH = (
    ROOT
    / "models"
    / "experimental"
    / "v1.2.0-multilingual"
    / "techmind_hybrid_v1_2_0_multilingual.joblib"
)


MODEL_PATH = Path(
    os.getenv(
        "TECHMIND_V12_MODEL_PATH",
        str(
            DEFAULT_MODEL_PATH
        )
    )
)


predictor: TechMindPredictor | None = None


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    global predictor

    predictor = TechMindPredictor(
        MODEL_PATH
    )

    yield

    predictor = None


app = FastAPI(

    title=(
        "TechMind API"
    ),

    description=(
        "Experimental multilingual API "
        "for technical content classification. "
        "TechMind v1.2.0-multilingual."
    ),

    version=API_VERSION,

    lifespan=lifespan,
)


def _get_predictor() -> TechMindPredictor:

    if predictor is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Model is not loaded."
            ),
        )

    return predictor


@app.get("/")
def root() -> dict[str, Any]:

    return {
        "service":
            "TechMind API",

        "api_version":
            API_VERSION,

        "model_version":
            MODEL_VERSION,

        "status":
            "experimental",

        "docs":
            "/docs",

        "health":
            "/health",

        "model_info":
            "/model-info",
    }


@app.get("/health")
def health() -> dict[str, Any]:

    loaded = (
        predictor is not None
    )

    return {
        "status":
            (
                "ok"
                if loaded
                else "loading"
            ),

        "model_loaded":
            loaded,

        "api_version":
            API_VERSION,

        "model_version":
            (
                predictor.version
                if loaded
                else MODEL_VERSION
            ),
    }


@app.get("/model-info")
def model_info() -> dict[str, Any]:

    model = (
        _get_predictor()
    )

    info = (
        model.model_info()
    )

    return {
        "api_version":
            API_VERSION,

        **info,
    }


@app.post(
    "/predict",
    response_model=PredictResponse,
)
def predict(
    request: PredictRequest,
) -> dict[str, Any]:

    model = (
        _get_predictor()
    )

    try:

        return model.predict(

            request.texts,

            include_explanation=(
                request.include_explanation
            ),

            explanation_top_n=(
                request.explanation_top_n
            ),

            top_k=(
                request.top_k
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except TypeError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
