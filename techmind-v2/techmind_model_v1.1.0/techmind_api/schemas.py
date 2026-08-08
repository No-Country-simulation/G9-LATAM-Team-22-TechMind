"""Esquemas de entrada y salida de la API TechMind."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


MAX_DOCUMENTOS_LOTE = 500
MAX_CARACTERES_TEXTO = 50000
MAX_TOP_N_EXPLICACION = 20
NUMERO_CATEGORIAS = 4


class PredictionRequest(BaseModel):
    """Solicitud de clasificación de contenido tecnológico."""

    textos: list[str] = Field(
        ...,
        min_length=1,
        max_length=MAX_DOCUMENTOS_LOTE,
        description=(
            "Lista de documentos tecnológicos "
            "que serán clasificados."
        )
    )

    incluir_explicacion: bool = Field(
        default=False,
        description=(
            "Incluye contribuciones locales de términos."
        )
    )

    top_n_explicacion: int = Field(
        default=8,
        ge=1,
        le=MAX_TOP_N_EXPLICACION,
        description=(
            "Número de términos incluidos "
            "en cada explicación."
        )
    )

    top_k: int | None = Field(
        default=None,
        ge=1,
        le=NUMERO_CATEGORIAS,
        description=(
            "Número de categorías devueltas "
            "en el ranking."
        )
    )


class RankingItem(BaseModel):
    position: int
    category: str
    score: float


class PredictionResult(BaseModel):
    request_id: str
    record_id: int
    timestamp_utc: str
    input_type: str
    text: str | None
    characters: int
    words: int
    valid_input: bool
    validation_message: str
    estado: str
    categoria_predicha: str | None
    segunda_categoria: str | None
    puntuacion_ganadora: float | None
    puntuacion_segunda: float | None
    margen_decision: float | None
    nivel_margen: str | None
    terminos_activos: int
    word_features_activas: int | None = None
    char_features_activas: int | None = None
    features_activas_total: int | None = None
    accion_recomendada: str
    requiere_revision: bool
    prediccion_utilizable: bool
    advertencias: list[str]
    ranking_categorias: list[RankingItem] | None
    explicacion: dict[str, Any] | None


class PredictionSummary(BaseModel):
    request_id: str
    timestamp_utc: str
    interface_version: str
    model_version: str | None = None
    model_name: str | None
    documents_received: int
    documents_accepted: int
    documents_review: int
    documents_rejected: int
    duration_seconds: float
    milliseconds_per_document: float
    explanations_included: bool
    margin_is_probability: bool


class PredictionResponse(BaseModel):
    resumen: PredictionSummary
    resultados: list[PredictionResult]


class HealthResponse(BaseModel):
    status: str
    ready: bool
    api_version: str
    model_name: str | None
    model_status: str | None
    model_sha256: str
    classes: list[str]
    tfidf_features: int
    word_features: int | None = None
    char_features: int | None = None
    total_features: int | None = None
    pipeline_steps: list[str]
    started_at_utc: str
    checked_at_utc: str


class ModelInfoResponse(BaseModel):
    api_version: str
    model_name: str | None
    model_status: str | None
    model_version: str | None
    model_sha256: str
    classes: list[str]
    tfidf_features: int
    word_features: int | None = None
    char_features: int | None = None
    total_features: int | None = None
    pipeline_steps: list[str]
    limits: dict[str, Any]
    margin_thresholds: dict[str, Any]
    margin_is_probability: bool
    optional_explanations: bool
    documentation: dict[str, str]


class RootResponse(BaseModel):
    name: str
    version: str
    status: str
    endpoints: dict[str, str]
