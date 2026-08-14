from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


class PredictRequest(BaseModel):

    texts: str | list[str] = Field(
        ...,
        description=(
            "Texto único o lista de textos "
            "para clasificar."
        ),
    )

    include_explanation: bool = Field(
        default=False,
        description=(
            "Incluye explicación diferencial "
            "basada en TF-IDF."
        ),
    )

    explanation_top_n: int = Field(
        default=8,
        ge=1,
        le=50,
        description=(
            "Número máximo de términos "
            "en la explicación."
        ),
    )

    top_k: int | None = Field(
        default=None,
        ge=1,
        le=4,
        description=(
            "Número de clases a devolver "
            "en el ranking."
        ),
    )


class PredictionItem(BaseModel):

    index: int

    text: Any

    valid_input: bool

    decision: str

    prediction: str | None

    second_category: str | None

    decision_margin: float | None

    domain_similarity_5nn: float | None

    tfidf_active_features: int

    reason: str | None

    score_top1: float | None = None

    score_top2: float | None = None

    top_k: list[dict[str, Any]] | None = None

    explanation: dict[str, Any] | None = None


class PredictResponse(BaseModel):

    model_version: str

    model_status: str

    n_inputs: int

    summary: dict[str, int]

    predictions: list[PredictionItem]
