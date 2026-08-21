from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import hashlib
import json
import time

import joblib
import numpy as np


INTERFACE_VERSION = "1.0.0"


# ==============================================================================
# UTILIDADES
# ==============================================================================

def _sha256(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """Calcula SHA-256 de un archivo."""

    digest = hashlib.sha256()

    with path.open("rb") as archivo:

        while True:

            bloque = archivo.read(
                chunk_size
            )

            if not bloque:
                break

            digest.update(
                bloque
            )

    return digest.hexdigest()


def _load_json(
    path: Path,
) -> dict[str, Any]:
    """Carga un JSON UTF-8."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as archivo:

        return json.load(
            archivo
        )


# ==============================================================================
# PREDICTOR
# ==============================================================================

class TechMindPredictor:
    """Clasificador independiente de contenido tecnológico."""

    def __init__(
        self,
        package_root: str | Path | None = None,
        verify_hash: bool = True,
    ) -> None:

        # ----------------------------------------------------------------------
        # PACKAGE ROOT
        # ----------------------------------------------------------------------

        if package_root is None:

            self.package_root = (
                Path(__file__)
                .resolve()
                .parents[1]
            )

        else:

            self.package_root = Path(
                package_root
            ).resolve()


        self.artifacts_dir = (
            self.package_root
            / "artifacts"
        )


        self.model_path = (
            self.artifacts_dir
            / "techmind_modelo_final.joblib"
        )


        self.metadata_path = (
            self.artifacts_dir
            / "techmind_modelo_final_metadata.json"
        )


        self.config_path = (
            self.artifacts_dir
            / "configuracion_inferencia.json"
        )


        self.contract_path = (
            self.artifacts_dir
            / "contrato_inferencia.json"
        )


        required_files = [
            self.model_path,
            self.metadata_path,
            self.config_path,
            self.contract_path,
        ]


        missing_files = [
            str(path)
            for path in required_files
            if not path.exists()
        ]


        if missing_files:

            raise FileNotFoundError(
                "Faltan archivos del paquete:\n"
                + "\n".join(
                    f"- {path}"
                    for path
                    in missing_files
                )
            )


        # ----------------------------------------------------------------------
        # METADATA / CONFIG / CONTRACT
        # ----------------------------------------------------------------------

        self.metadata = _load_json(
            self.metadata_path
        )

        self.config = _load_json(
            self.config_path
        )

        self.contract = _load_json(
            self.contract_path
        )


        self.interface_version = str(
            self.config.get(
                "interface_version",
                INTERFACE_VERSION,
            )
        )


        self.model_version = str(
            self.metadata.get(
                "version",
                self.config.get(
                    "model_version",
                    "1.1.0",
                ),
            )
        )


        self.model_name = str(
            self.metadata.get(
                "model_name",
                self.metadata.get(
                    "modelo",
                    (
                        "TF-IDF Word + Char 3-6 "
                        "+ SGDClassifier optimizado"
                    ),
                ),
            )
        )


        self.model_status = str(
            self.metadata.get(
                "status",
                self.metadata.get(
                    "estado",
                    "ready",
                ),
            )
        )


        # ----------------------------------------------------------------------
        # HASH
        # ----------------------------------------------------------------------

        self.model_sha256 = _sha256(
            self.model_path
        )


        expected_sha256 = (
            self.metadata.get(
                "sha256"
            )
            or
            self.metadata.get(
                "model_sha256"
            )
            or
            self.metadata.get(
                "sha256_modelo"
            )
            or
            self.config.get(
                "model_sha256"
            )
        )


        if (
            verify_hash
            and expected_sha256
            and self.model_sha256
            != str(expected_sha256)
        ):

            raise RuntimeError(
                "La firma SHA-256 del modelo "
                "no coincide con la registrada."
            )


        # ----------------------------------------------------------------------
        # CARGAR MODELO
        # ----------------------------------------------------------------------

        self.model = joblib.load(
            self.model_path
        )


        if not hasattr(
            self.model,
            "named_steps",
        ):

            raise TypeError(
                "El artefacto cargado no es "
                "un Pipeline compatible."
            )


        pipeline_steps = list(
            self.model.named_steps.keys()
        )


        required_steps = {
            "features",
            "clasificador",
        }


        if not required_steps.issubset(
            set(pipeline_steps)
        ):

            raise RuntimeError(
                "Pipeline v1.1.0 incompatible. "
                "Se requieren los pasos "
                "'features' y 'clasificador'. "
                f"Encontrados: {pipeline_steps}"
            )


        # ----------------------------------------------------------------------
        # FEATURE UNION
        # ----------------------------------------------------------------------

        self.feature_union = (
            self.model
            .named_steps[
                "features"
            ]
        )


        transformadores = dict(
            self.feature_union
            .transformer_list
        )


        if (
            "word" not in transformadores
            or
            "char" not in transformadores
        ):

            raise RuntimeError(
                "FeatureUnion incompatible. "
                "Se requieren transformadores "
                "'word' y 'char'."
            )


        self.word_vectorizer = (
            transformadores[
                "word"
            ]
        )


        self.char_vectorizer = (
            transformadores[
                "char"
            ]
        )


        self.classifier = (
            self.model
            .named_steps[
                "clasificador"
            ]
        )


        # ----------------------------------------------------------------------
        # VOCABULARIOS
        # ----------------------------------------------------------------------

        self.word_feature_names = np.asarray(
            self.word_vectorizer
            .get_feature_names_out()
        )


        self.char_feature_names = np.asarray(
            self.char_vectorizer
            .get_feature_names_out()
        )


        self.word_feature_count = int(
            len(
                self.word_feature_names
            )
        )


        self.char_feature_count = int(
            len(
                self.char_feature_names
            )
        )


        self.total_feature_count = int(
            self.word_feature_count
            + self.char_feature_count
        )


        # Alias retrocompatible:
        # main.py todavía solicita tfidf_features.
        self.feature_names = np.concatenate([
            self.word_feature_names,
            self.char_feature_names,
        ])


        self.feature_types = np.asarray(
            (
                ["word"]
                * self.word_feature_count
            )
            +
            (
                ["char"]
                * self.char_feature_count
            )
        )


        # ----------------------------------------------------------------------
        # CLASES
        # ----------------------------------------------------------------------

        self.classes = np.asarray(
            self.classifier.classes_
        )


        if len(
            self.classes
        ) < 2:

            raise RuntimeError(
                "El modelo debe contener "
                "al menos dos clases."
            )


        # ----------------------------------------------------------------------
        # VALIDACIÓN DE COEFICIENTES
        # ----------------------------------------------------------------------

        if not hasattr(
            self.classifier,
            "coef_",
        ):

            raise RuntimeError(
                "El clasificador no expone coef_. "
                "La explicabilidad lineal no "
                "está disponible."
            )


        coef_shape = (
            self.classifier
            .coef_
            .shape
        )


        if (
            coef_shape[1]
            != self.total_feature_count
        ):

            raise RuntimeError(
                "El número de coeficientes "
                "no coincide con Word + Char. "
                f"Coeficientes={coef_shape[1]}, "
                f"features={self.total_feature_count}."
            )


        # ----------------------------------------------------------------------
        # MÁRGENES
        # ----------------------------------------------------------------------

        margin_thresholds = (
            self.config.get(
                "margin_thresholds",
                {},
            )
        )


        operational_config = (
            self.config.get(
                "operational",
                {},
            )
        )


        self.review_margin = float(
            margin_thresholds.get(
                "review",
                operational_config.get(
                    "review_margin",
                    0.0,
                ),
            )
        )


        self.margin_p10 = float(
            margin_thresholds.get(
                "p10",
                self.review_margin,
            )
        )


        self.margin_p25 = float(
            margin_thresholds.get(
                "p25",
                self.margin_p10,
            )
        )


        self.margin_p50 = float(
            margin_thresholds.get(
                "p50",
                self.margin_p25,
            )
        )


        self.margin_p90 = float(
            margin_thresholds.get(
                "p90",
                self.margin_p50,
            )
        )


        # ----------------------------------------------------------------------
        # COBERTURA
        # ----------------------------------------------------------------------

        coverage = self.config.get(
            "coverage",
            {}
        )


        self.few_terms_threshold = int(
            coverage.get(
                "few_features_threshold",
                operational_config.get(
                    "few_features_threshold",
                    1,
                ),
            )
        )


        self.reject_if_total_features = int(
            coverage.get(
                "reject_if_total_features",
                operational_config.get(
                    "reject_if_total_features",
                    0,
                ),
            )
        )


        # ----------------------------------------------------------------------
        # LÍMITES
        # ----------------------------------------------------------------------

        limits = self.config.get(
            "limits",
            {}
        )


        self.max_batch_size = int(
            limits.get(
                "max_batch_size",
                500,
            )
        )


        self.max_characters_per_document = int(
            limits.get(
                "max_characters_per_document",
                limits.get(
                    "max_characters",
                    50000,
                ),
            )
        )


    # ==========================================================================
    # HEALTH
    # ==========================================================================

    def health(
        self,
    ) -> dict[str, Any]:
        """Devuelve información técnica del modelo."""

        return {
            "status": "ok",

            "interface_version": (
                self.interface_version
            ),

            "model_version": (
                self.model_version
            ),

            "model_name": (
                self.model_name
            ),

            "model_status": (
                self.model_status
            ),

            "classes": [
                str(value)
                for value
                in self.classes
            ],

            # --------------------------------------------------------------
            # Alias requerido por FastAPI v1.0.
            # Ahora representa Word + Char.
            # --------------------------------------------------------------

            "tfidf_features": int(
                self.total_feature_count
            ),

            # --------------------------------------------------------------
            # Información ampliada v1.1.
            # --------------------------------------------------------------

            "word_features": int(
                self.word_feature_count
            ),

            "char_features": int(
                self.char_feature_count
            ),

            "total_features": int(
                self.total_feature_count
            ),

            "model_sha256": (
                self.model_sha256
            ),

            "pipeline_steps": list(
                self.model
                .named_steps
                .keys()
            ),

            "architecture": (
                "TF-IDF Word + "
                "TF-IDF Char 3-6 + "
                "SGDClassifier"
            ),

            "margin_is_probability": False,
        }


    # ==========================================================================
    # INPUTS
    # ==========================================================================

    def _prepare_inputs(
        self,
        texts: str | Iterable[str],
    ) -> list[Any]:
        """Normaliza el contenedor de entrada."""

        if isinstance(
            texts,
            str,
        ):

            documents = [
                texts
            ]


        elif isinstance(
            texts,
            np.ndarray,
        ):

            if texts.ndim != 1:

                raise ValueError(
                    "El arreglo NumPy debe "
                    "ser unidimensional."
                )

            documents = (
                texts.tolist()
            )


        elif isinstance(
            texts,
            (
                list,
                tuple,
            ),
        ):

            documents = list(
                texts
            )


        else:

            raise TypeError(
                "La entrada debe ser un texto, "
                "lista, tupla o arreglo "
                "unidimensional."
            )


        if not documents:

            raise ValueError(
                "La colección de textos "
                "está vacía."
            )


        if (
            len(documents)
            > self.max_batch_size
        ):

            raise ValueError(
                "El lote excede el máximo de "
                f"{self.max_batch_size} documentos."
            )


        return documents


    # ==========================================================================
    # VALIDACIÓN
    # ==========================================================================

    def _validate_text(
        self,
        value: Any,
    ) -> dict[str, Any]:
        """Valida un documento individual."""

        input_type = type(
            value
        ).__name__


        if not isinstance(
            value,
            str,
        ):

            return {
                "valid": False,
                "text": None,
                "input_type": input_type,
                "message": (
                    "El documento debe ser texto."
                ),
            }


        text = value.strip()


        if not text:

            return {
                "valid": False,
                "text": text,
                "input_type": input_type,
                "message": (
                    "El texto está vacío."
                ),
            }


        if (
            len(text)
            > self.max_characters_per_document
        ):

            return {
                "valid": False,
                "text": text,
                "input_type": input_type,
                "message": (
                    "El documento excede el "
                    "máximo de caracteres permitido."
                ),
            }


        return {
            "valid": True,
            "text": text,
            "input_type": input_type,
            "message": (
                "Inferencia completada."
            ),
        }


    # ==========================================================================
    # MARGEN
    # ==========================================================================

    def _margin_level(
        self,
        margin: float,
    ) -> str:
        """Asigna un nivel descriptivo al margen."""

        if margin <= self.margin_p10:
            return "Crítica"

        if margin <= self.margin_p25:
            return "Baja"

        if margin <= self.margin_p50:
            return "Media"

        if margin <= self.margin_p90:
            return "Alta"

        return "Muy alta"


    # ==========================================================================
    # DECISIÓN OPERACIONAL
    # ==========================================================================

    def _operational_decision(
        self,
        margin: float,
        total_features: int,
        word_features: int,
        char_features: int,
    ) -> dict[str, Any]:
        """Aplica la política calibrada de v1.1.0."""

        warnings: list[str] = []


        # ------------------------------------------------------------------
        # SIN COBERTURA
        # ------------------------------------------------------------------

        if (
            total_features
            <= self.reject_if_total_features
        ):

            return {
                "estado": "rechazada",
                "accion": (
                    "No utilizar la predicción"
                ),
                "requiere_revision": False,
                "prediccion_utilizable": False,
                "advertencias": [
                    (
                        "Sin cobertura de "
                        "características."
                    )
                ],
            }


        # ------------------------------------------------------------------
        # INFORMACIÓN DE COBERTURA
        # ------------------------------------------------------------------

        if word_features == 0:

            warnings.append(
                "La cobertura depende únicamente "
                "de n-gramas de caracteres."
            )


        if (
            total_features
            <= self.few_terms_threshold
        ):

            warnings.append(
                "Cobertura reducida de "
                "características."
            )


        # ------------------------------------------------------------------
        # MARGEN
        # ------------------------------------------------------------------

        if (
            margin
            < self.review_margin
        ):

            warnings.append(
                "El margen de decisión "
                "es reducido."
            )


        # ------------------------------------------------------------------
        # REVISIÓN
        # ------------------------------------------------------------------

        if (
            margin
            < self.review_margin
            or
            total_features
            <= self.few_terms_threshold
        ):

            return {
                "estado": "revision",
                "accion": (
                    "Revisión humana recomendada"
                ),
                "requiere_revision": True,
                "prediccion_utilizable": True,
                "advertencias": warnings,
            }


        # ------------------------------------------------------------------
        # ACEPTADA
        # ------------------------------------------------------------------

        return {
            "estado": "aceptada",
            "accion": (
                "Predicción utilizable "
                "automáticamente"
            ),
            "requiere_revision": False,
            "prediccion_utilizable": True,
            "advertencias": warnings,
        }


    # ==========================================================================
    # SCORES
    # ==========================================================================

    def _normalize_scores(
        self,
        scores: np.ndarray,
    ) -> np.ndarray:
        """Normaliza decision_function a matriz 2D."""

        scores = np.asarray(
            scores
        )


        if scores.ndim == 1:

            if len(
                self.classes
            ) == 2:

                scores = np.column_stack([
                    -scores,
                    scores,
                ])

            else:

                scores = scores.reshape(
                    1,
                    -1,
                )


        return scores


    # ==========================================================================
    # RANKING
    # ==========================================================================

    def _ranking(
        self,
        scores: np.ndarray,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Genera ranking de categorías."""

        orden = np.argsort(
            scores
        )[::-1][
            :top_k
        ]


        return [
            {
                "position": int(
                    posicion
                ),

                "category": str(
                    self.classes[
                        indice
                    ]
                ),

                "score": float(
                    scores[
                        indice
                    ]
                ),
            }

            for posicion, indice
            in enumerate(
                orden,
                start=1,
            )
        ]


    # ==========================================================================
    # EXPLICABILIDAD
    # ==========================================================================

    def _explain_vector(
        self,
        vector,
        winner_index: int,
        second_index: int,
        top_n: int,
    ) -> dict[str, Any]:
        """
        Explica una predicción lineal sobre
        FeatureUnion Word + Char.
        """

        vector = vector.getrow(
            0
        )


        indices = (
            vector.indices
        )

        values = (
            vector.data
        )


        if len(indices) == 0:

            return {
                "positive_terms": [],
                "negative_terms": [],
                "differential_terms": [],
                "warning": (
                    "No existen características "
                    "activas para explicar."
                ),
            }


        winner_coef = (
            self.classifier
            .coef_[
                winner_index,
                indices,
            ]
        )


        second_coef = (
            self.classifier
            .coef_[
                second_index,
                indices,
            ]
        )


        contributions = (
            values
            * winner_coef
        )


        differential = (
            values
            * (
                winner_coef
                - second_coef
            )
        )


        records = []


        for local_index, feature_index in enumerate(
            indices
        ):

            records.append({
                "feature_index": int(
                    feature_index
                ),

                "term": str(
                    self.feature_names[
                        feature_index
                    ]
                ),

                "feature_type": str(
                    self.feature_types[
                        feature_index
                    ]
                ),

                "tfidf": float(
                    values[
                        local_index
                    ]
                ),

                "coefficient": float(
                    winner_coef[
                        local_index
                    ]
                ),

                "contribution": float(
                    contributions[
                        local_index
                    ]
                ),

                "differential": float(
                    differential[
                        local_index
                    ]
                ),
            })


        # ------------------------------------------------------------------
        # POSITIVAS
        # ------------------------------------------------------------------

        positive = sorted(
            (
                item
                for item
                in records
                if item[
                    "contribution"
                ] > 0
            ),
            key=lambda item: (
                item[
                    "contribution"
                ]
            ),
            reverse=True,
        )[:top_n]


        positive_terms = [
            {
                "term": item["term"],
                "feature_type": (
                    item[
                        "feature_type"
                    ]
                ),
                "tfidf": item["tfidf"],
                "coefficient": (
                    item[
                        "coefficient"
                    ]
                ),
                "contribution": (
                    item[
                        "contribution"
                    ]
                ),
            }

            for item
            in positive
        ]


        # ------------------------------------------------------------------
        # NEGATIVAS
        # ------------------------------------------------------------------

        negative = sorted(
            (
                item
                for item
                in records
                if item[
                    "contribution"
                ] < 0
            ),
            key=lambda item: (
                item[
                    "contribution"
                ]
            ),
        )[:top_n]


        negative_terms = [
            {
                "term": item["term"],
                "feature_type": (
                    item[
                        "feature_type"
                    ]
                ),
                "tfidf": item["tfidf"],
                "coefficient": (
                    item[
                        "coefficient"
                    ]
                ),
                "contribution": (
                    item[
                        "contribution"
                    ]
                ),
            }

            for item
            in negative
        ]


        # ------------------------------------------------------------------
        # DIFERENCIALES
        # ------------------------------------------------------------------

        differential_sorted = sorted(
            records,
            key=lambda item: abs(
                item[
                    "differential"
                ]
            ),
            reverse=True,
        )[:top_n]


        winner_class = str(
            self.classes[
                winner_index
            ]
        )


        second_class = str(
            self.classes[
                second_index
            ]
        )


        differential_terms = [
            {
                "term": item["term"],

                "feature_type": (
                    item[
                        "feature_type"
                    ]
                ),

                "contribution": (
                    item[
                        "differential"
                    ]
                ),

                "favours": (
                    winner_class
                    if item[
                        "differential"
                    ] >= 0
                    else second_class
                ),
            }

            for item
            in differential_sorted
        ]


        return {
            "positive_terms": (
                positive_terms
            ),

            "negative_terms": (
                negative_terms
            ),

            "differential_terms": (
                differential_terms
            ),

            "warning": (
                "Las contribuciones describen "
                "el comportamiento matemático "
                "del modelo, no causalidad."
            ),
        }


    # ==========================================================================
    # PREDICT
    # ==========================================================================

    def predict(
        self,
        texts: str | Iterable[str],
        include_explanation: bool = False,
        explanation_top_n: int = 8,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        """Clasifica uno o varios documentos."""

        start_time = (
            time.perf_counter()
        )


        documents = (
            self._prepare_inputs(
                texts
            )
        )


        if not isinstance(
            include_explanation,
            bool,
        ):

            raise TypeError(
                "include_explanation "
                "debe ser booleano."
            )


        explanation_top_n = int(
            explanation_top_n
        )


        if explanation_top_n <= 0:

            raise ValueError(
                "explanation_top_n debe "
                "ser mayor que cero."
            )


        if top_k is None:

            top_k = len(
                self.classes
            )


        top_k = int(
            top_k
        )


        if not (
            1
            <= top_k
            <= len(
                self.classes
            )
        ):

            raise ValueError(
                "top_k está fuera del "
                "rango permitido."
            )


        request_id = str(
            uuid4()
        )


        timestamp = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="milliseconds"
        )


        results: list[
            dict[str, Any]
        ] = []


        valid_positions: list[
            int
        ] = []


        valid_texts: list[
            str
        ] = []


        # ------------------------------------------------------------------
        # VALIDACIÓN
        # ------------------------------------------------------------------

        for index, value in enumerate(
            documents
        ):

            validation = (
                self._validate_text(
                    value
                )
            )


            text_for_result = (
                validation[
                    "text"
                ]
            )


            result = {
                "request_id": request_id,
                "record_id": int(
                    index
                ),
                "timestamp_utc": timestamp,

                "input_type": (
                    validation[
                        "input_type"
                    ]
                ),

                "text": (
                    text_for_result
                ),

                "characters": (
                    len(
                        text_for_result
                    )
                    if isinstance(
                        text_for_result,
                        str,
                    )
                    else 0
                ),

                "words": (
                    len(
                        text_for_result
                        .split()
                    )
                    if isinstance(
                        text_for_result,
                        str,
                    )
                    else 0
                ),

                "valid_input": bool(
                    validation[
                        "valid"
                    ]
                ),

                "validation_message": (
                    validation[
                        "message"
                    ]
                ),

                "estado": "rechazada",

                "categoria_predicha": None,

                "segunda_categoria": None,

                "puntuacion_ganadora": None,

                "puntuacion_segunda": None,

                "margen_decision": None,

                "nivel_margen": None,

                # ------------------------------------------------------
                # COMPATIBILIDAD v1.0
                # ------------------------------------------------------

                "terminos_activos": 0,

                # ------------------------------------------------------
                # NUEVO v1.1
                # ------------------------------------------------------

                "word_features_activas": 0,

                "char_features_activas": 0,

                "features_activas_total": 0,

                "accion_recomendada": (
                    "No utilizar la predicción"
                ),

                "requiere_revision": False,

                "prediccion_utilizable": False,

                "advertencias": [],

                "ranking_categorias": [],

                "explicacion": (
                    None
                    if not include_explanation
                    else {
                        "positive_terms": [],
                        "negative_terms": [],
                        "differential_terms": [],
                        "warning": (
                            "No existe una predicción "
                            "utilizable para explicar."
                        ),
                    }
                ),
            }


            results.append(
                result
            )


            if validation[
                "valid"
            ]:

                valid_positions.append(
                    index
                )

                valid_texts.append(
                    validation[
                        "text"
                    ]
                )


        # ------------------------------------------------------------------
        # INFERENCIA
        # ------------------------------------------------------------------

        if valid_texts:

            combined_matrix = (
                self.feature_union
                .transform(
                    valid_texts
                )
            )


            word_matrix = (
                self.word_vectorizer
                .transform(
                    valid_texts
                )
            )


            char_matrix = (
                self.char_vectorizer
                .transform(
                    valid_texts
                )
            )


            scores_matrix = (
                self._normalize_scores(
                    self.model
                    .decision_function(
                        valid_texts
                    )
                )
            )


            for local_position, result_position in enumerate(
                valid_positions
            ):

                combined_vector = (
                    combined_matrix[
                        local_position
                    ]
                )


                word_features = int(
                    word_matrix[
                        local_position
                    ].getnnz()
                )


                char_features = int(
                    char_matrix[
                        local_position
                    ].getnnz()
                )


                total_features = int(
                    combined_vector.getnnz()
                )


                # ------------------------------------------------------
                # SIN COBERTURA
                # ------------------------------------------------------

                if (
                    total_features
                    <= self.reject_if_total_features
                ):

                    results[
                        result_position
                    ].update({
                        "estado": (
                            "rechazada"
                        ),

                        "validation_message": (
                            "Texto válido, pero "
                            "sin cobertura de "
                            "características."
                        ),

                        "word_features_activas": (
                            word_features
                        ),

                        "char_features_activas": (
                            char_features
                        ),

                        "features_activas_total": (
                            total_features
                        ),

                        "terminos_activos": (
                            total_features
                        ),

                        "accion_recomendada": (
                            "No utilizar "
                            "la predicción"
                        ),

                        "requiere_revision": False,

                        "prediccion_utilizable": False,

                        "advertencias": [
                            (
                                "Sin cobertura de "
                                "características."
                            )
                        ],
                    })

                    continue


                # ------------------------------------------------------
                # SCORES
                # ------------------------------------------------------

                scores = (
                    scores_matrix[
                        local_position
                    ]
                )


                order = np.argsort(
                    scores
                )[::-1]


                winner_index = int(
                    order[
                        0
                    ]
                )


                second_index = int(
                    order[
                        1
                    ]
                )


                category = str(
                    self.classes[
                        winner_index
                    ]
                )


                second_category = str(
                    self.classes[
                        second_index
                    ]
                )


                winner_score = float(
                    scores[
                        winner_index
                    ]
                )


                second_score = float(
                    scores[
                        second_index
                    ]
                )


                margin = float(
                    winner_score
                    - second_score
                )


                level = (
                    self._margin_level(
                        margin
                    )
                )


                decision = (
                    self._operational_decision(
                        margin=margin,
                        total_features=(
                            total_features
                        ),
                        word_features=(
                            word_features
                        ),
                        char_features=(
                            char_features
                        ),
                    )
                )


                ranking = (
                    self._ranking(
                        scores,
                        top_k=top_k,
                    )
                )


                explanation = None


                if include_explanation:

                    explanation = (
                        self._explain_vector(
                            vector=(
                                combined_vector
                            ),
                            winner_index=(
                                winner_index
                            ),
                            second_index=(
                                second_index
                            ),
                            top_n=(
                                explanation_top_n
                            ),
                        )
                    )


                results[
                    result_position
                ].update({
                    "validation_message": (
                        "Inferencia completada."
                    ),

                    "estado": (
                        decision[
                            "estado"
                        ]
                    ),

                    "categoria_predicha": (
                        category
                    ),

                    "segunda_categoria": (
                        second_category
                    ),

                    "puntuacion_ganadora": (
                        winner_score
                    ),

                    "puntuacion_segunda": (
                        second_score
                    ),

                    "margen_decision": (
                        margin
                    ),

                    "nivel_margen": (
                        level
                    ),

                    # --------------------------------------------------
                    # COMPATIBILIDAD:
                    # ahora significa features Word + Char activas.
                    # --------------------------------------------------

                    "terminos_activos": (
                        total_features
                    ),

                    # --------------------------------------------------
                    # v1.1
                    # --------------------------------------------------

                    "word_features_activas": (
                        word_features
                    ),

                    "char_features_activas": (
                        char_features
                    ),

                    "features_activas_total": (
                        total_features
                    ),

                    "accion_recomendada": (
                        decision[
                            "accion"
                        ]
                    ),

                    "requiere_revision": (
                        decision[
                            "requiere_revision"
                        ]
                    ),

                    "prediccion_utilizable": (
                        decision[
                            "prediccion_utilizable"
                        ]
                    ),

                    "advertencias": (
                        decision[
                            "advertencias"
                        ]
                    ),

                    "ranking_categorias": (
                        ranking
                    ),

                    "explicacion": (
                        explanation
                    ),
                })


        # ------------------------------------------------------------------
        # RESUMEN
        # ------------------------------------------------------------------

        duration_seconds = float(
            time.perf_counter()
            - start_time
        )


        accepted = sum(
            result[
                "estado"
            ] == "aceptada"
            for result
            in results
        )


        review = sum(
            result[
                "estado"
            ] == "revision"
            for result
            in results
        )


        rejected = sum(
            result[
                "estado"
            ] == "rechazada"
            for result
            in results
        )


        document_count = len(
            results
        )


        milliseconds_per_document = (
            duration_seconds
            * 1000
            / document_count
            if document_count
            else 0.0
        )


        return {
            "resumen": {
                "request_id": request_id,

                "timestamp_utc": timestamp,

                "interface_version": (
                    self.interface_version
                ),

                "model_version": (
                    self.model_version
                ),

                "model_name": (
                    self.model_name
                ),

                "documents_received": (
                    document_count
                ),

                "documents_accepted": int(
                    accepted
                ),

                "documents_review": int(
                    review
                ),

                "documents_rejected": int(
                    rejected
                ),

                "duration_seconds": (
                    duration_seconds
                ),

                "milliseconds_per_document": (
                    milliseconds_per_document
                ),

                "explanations_included": (
                    include_explanation
                ),

                "margin_is_probability": False,
            },

            "resultados": results,
        }
