"""Interfaz independiente de inferencia para TechMind v2.0."""

from __future__ import annotations

import hashlib
import json
import time

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import joblib
import numpy as np


__version__ = "1.0.0"


def _sha256(path: Path) -> str:
    """Calcula la firma SHA-256 de un archivo."""

    digest = hashlib.sha256()

    with path.open("rb") as file:

        for block in iter(
            lambda: file.read(8192),
            b""
        ):
            digest.update(block)

    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    """Carga un archivo JSON."""

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


class TechMindPredictor:
    """Clasificador independiente de contenido tecnológico."""

    def __init__(
        self,
        package_root: str | Path | None = None,
        verify_hash: bool = True
    ) -> None:
        """
        Carga el modelo y la configuración del paquete.

        Parameters
        ----------
        package_root:
            Directorio raíz del paquete exportado.

        verify_hash:
            Comprueba que la firma del modelo coincide
            con la registrada en la configuración.
        """

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
            self.contract_path
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
                    for path in missing_files
                )
            )

        self.metadata = _load_json(
            self.metadata_path
        )

        self.config = _load_json(
            self.config_path
        )

        self.contract = _load_json(
            self.contract_path
        )

        self.model_sha256 = _sha256(
            self.model_path
        )

        expected_hash = self.config.get(
            "sha256_modelo"
        )

        if (
            verify_hash
            and expected_hash
            and self.model_sha256
            != expected_hash
        ):

            raise RuntimeError(
                "La firma SHA-256 del modelo "
                "no coincide con la configuración."
            )

        self.model = joblib.load(
            self.model_path
        )

        if not hasattr(
            self.model,
            "named_steps"
        ):

            raise TypeError(
                "El archivo cargado no contiene "
                "un Pipeline compatible."
            )

        required_steps = {
            "tfidf",
            "clasificador"
        }

        missing_steps = (
            required_steps
            - set(
                self.model
                .named_steps
                .keys()
            )
        )

        if missing_steps:

            raise ValueError(
                "El pipeline no contiene los pasos: "
                f"{sorted(missing_steps)}"
            )

        self.vectorizer = (
            self.model
            .named_steps["tfidf"]
        )

        self.classifier = (
            self.model
            .named_steps["clasificador"]
        )

        self.classes = np.asarray(
            self.classifier.classes_
        )

        self.feature_names = (
            self.vectorizer
            .get_feature_names_out()
        )

        if len(self.classes) < 2:

            raise ValueError(
                "El modelo debe contener "
                "al menos dos categorías."
            )

        if not hasattr(
            self.classifier,
            "coef_"
        ):

            raise TypeError(
                "El clasificador no expone coeficientes."
            )

        thresholds = self.config.get(
            "umbrales_margen_descriptivos",
            {}
        )

        self.margin_p10 = float(
            thresholds.get(
                "p10",
                0.0
            )
        )

        self.margin_p25 = float(
            thresholds.get(
                "p25",
                self.margin_p10
            )
        )

        self.margin_p50 = float(
            thresholds.get(
                "p50",
                self.margin_p25
            )
        )

        self.margin_p90 = float(
            thresholds.get(
                "p90",
                self.margin_p50
            )
        )

        limits = self.config.get(
            "limites_entrada",
            {}
        )

        self.max_batch_size = int(
            limits.get(
                "max_documentos_lote",
                500
            )
        )

        self.min_characters = int(
            limits.get(
                "min_caracteres",
                2
            )
        )

        self.max_characters = int(
            limits.get(
                "max_caracteres",
                50000
            )
        )

        self.min_words_automatic = int(
            limits.get(
                "min_palabras_automatico",
                3
            )
        )

        self.few_terms_threshold = int(
            self.config.get(
                "umbral_pocos_terminos",
                1
            )
        )


    def health(self) -> dict[str, Any]:
        """Devuelve información técnica del modelo."""

        return {
            "status": "ok",
            "interface_version": __version__,
            "model_name": self.metadata.get(
                "modelo"
            ),
            "model_status": self.metadata.get(
                "estado"
            ),
            "classes": [
                str(value)
                for value in self.classes
            ],
            "tfidf_features": int(
                len(self.feature_names)
            ),
            "model_sha256": self.model_sha256,
            "pipeline_steps": list(
                self.model
                .named_steps
                .keys()
            )
        }


    def _prepare_inputs(
        self,
        texts: str | Iterable[str]
    ) -> list[Any]:
        """Normaliza el contenedor de entrada."""

        if isinstance(texts, str):

            documents = [texts]

        elif isinstance(texts, np.ndarray):

            if texts.ndim != 1:

                raise ValueError(
                    "El arreglo NumPy debe "
                    "ser unidimensional."
                )

            documents = texts.tolist()

        elif isinstance(
            texts,
            (
                list,
                tuple
            )
        ):

            documents = list(texts)

        else:

            raise TypeError(
                "La entrada debe ser un texto, "
                "lista, tupla o arreglo unidimensional."
            )

        if not documents:

            raise ValueError(
                "La colección de textos está vacía."
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


    def _validate_text(
        self,
        value: Any
    ) -> dict[str, Any]:
        """Valida una entrada individual."""

        if value is None:

            return {
                "valid": False,
                "text": None,
                "message": "La entrada es nula.",
                "characters": 0,
                "words": 0,
                "input_type": "NoneType"
            }

        if not isinstance(
            value,
            str
        ):

            return {
                "valid": False,
                "text": None,
                "message": (
                    "La entrada debe ser "
                    "de tipo texto."
                ),
                "characters": 0,
                "words": 0,
                "input_type": (
                    type(value).__name__
                )
            }

        clean_text = value.strip()

        characters = len(
            clean_text
        )

        words = len(
            clean_text.split()
        )

        if not clean_text:

            return {
                "valid": False,
                "text": "",
                "message": "El texto está vacío.",
                "characters": 0,
                "words": 0,
                "input_type": "str"
            }

        if (
            characters
            < self.min_characters
        ):

            return {
                "valid": False,
                "text": clean_text,
                "message": (
                    "El texto es demasiado corto."
                ),
                "characters": characters,
                "words": words,
                "input_type": "str"
            }

        if (
            characters
            > self.max_characters
        ):

            return {
                "valid": False,
                "text": clean_text,
                "message": (
                    "El texto excede el máximo "
                    "de caracteres permitido."
                ),
                "characters": characters,
                "words": words,
                "input_type": "str"
            }

        return {
            "valid": True,
            "text": clean_text,
            "message": "Entrada válida.",
            "characters": characters,
            "words": words,
            "input_type": "str"
        }


    def _margin_level(
        self,
        margin: float
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


    def _operational_decision(
        self,
        level: str,
        active_terms: int,
        words: int
    ) -> dict[str, Any]:
        """Asigna una acción operativa provisional."""

        warnings: list[str] = []

        if active_terms <= 0:

            return {
                "status": "rechazada",
                "action": (
                    "Solicitar más contexto "
                    "o revisión humana"
                ),
                "requires_review": True,
                "usable": False,
                "warnings": [
                    (
                        "No se reconocieron términos "
                        "del vocabulario."
                    )
                ]
            }

        if (
            active_terms
            <= self.few_terms_threshold
        ):

            warnings.append(
                "Cobertura reducida del vocabulario."
            )

        if (
            words
            < self.min_words_automatic
        ):

            warnings.append(
                "El texto contiene pocas palabras."
            )

        if level == "Crítica":

            warnings.append(
                "Las dos categorías principales "
                "tienen puntuaciones muy cercanas."
            )

            return {
                "status": "revision",
                "action": (
                    "Revisión humana prioritaria"
                ),
                "requires_review": True,
                "usable": True,
                "warnings": warnings
            }

        if level == "Baja":

            warnings.append(
                "El margen de decisión es reducido."
            )

            return {
                "status": "revision",
                "action": (
                    "Revisión humana recomendada"
                ),
                "requires_review": True,
                "usable": True,
                "warnings": warnings
            }

        if warnings:

            return {
                "status": "revision",
                "action": (
                    "Revisión humana recomendada"
                ),
                "requires_review": True,
                "usable": True,
                "warnings": warnings
            }

        if level == "Media":

            return {
                "status": "aceptada",
                "action": (
                    "Predicción automática "
                    "con monitoreo"
                ),
                "requires_review": False,
                "usable": True,
                "warnings": []
            }

        return {
            "status": "aceptada",
            "action": (
                "Predicción automática"
            ),
            "requires_review": False,
            "usable": True,
            "warnings": []
        }


    def _explain_vector(
        self,
        vector: Any,
        predicted_index: int,
        alternative_index: int,
        top_n: int
    ) -> dict[str, Any]:
        """Genera una explicación local compacta."""

        vector = vector.tocsr()

        active_indices = vector.indices
        tfidf_values = vector.data

        if len(active_indices) == 0:

            return {
                "positive_terms": [],
                "negative_terms": [],
                "differential_terms": [],
                "warning": (
                    "No existen términos activos."
                )
            }

        terms = self.feature_names[
            active_indices
        ]

        predicted_coefficients = (
            self.classifier.coef_[
                predicted_index,
                active_indices
            ]
        )

        alternative_coefficients = (
            self.classifier.coef_[
                alternative_index,
                active_indices
            ]
        )

        contributions = (
            tfidf_values
            * predicted_coefficients
        )

        differential = (
            tfidf_values
            * (
                predicted_coefficients
                - alternative_coefficients
            )
        )

        positive_order = np.argsort(
            contributions
        )[::-1]

        negative_order = np.argsort(
            contributions
        )

        differential_order = np.argsort(
            np.abs(differential)
        )[::-1]

        positive_terms = []

        for local_index in positive_order:

            if contributions[
                local_index
            ] <= 0:

                continue

            positive_terms.append({
                "term": str(
                    terms[local_index]
                ),
                "tfidf": float(
                    tfidf_values[
                        local_index
                    ]
                ),
                "coefficient": float(
                    predicted_coefficients[
                        local_index
                    ]
                ),
                "contribution": float(
                    contributions[
                        local_index
                    ]
                )
            })

            if (
                len(positive_terms)
                >= top_n
            ):
                break

        negative_terms = []

        for local_index in negative_order:

            if contributions[
                local_index
            ] >= 0:

                continue

            negative_terms.append({
                "term": str(
                    terms[local_index]
                ),
                "tfidf": float(
                    tfidf_values[
                        local_index
                    ]
                ),
                "coefficient": float(
                    predicted_coefficients[
                        local_index
                    ]
                ),
                "contribution": float(
                    contributions[
                        local_index
                    ]
                )
            })

            if (
                len(negative_terms)
                >= top_n
            ):
                break

        differential_terms = []

        for local_index in differential_order:

            value = float(
                differential[
                    local_index
                ]
            )

            if value == 0:
                continue

            differential_terms.append({
                "term": str(
                    terms[local_index]
                ),
                "contribution": value,
                "favours": (
                    str(
                        self.classes[
                            predicted_index
                        ]
                    )
                    if value > 0
                    else str(
                        self.classes[
                            alternative_index
                        ]
                    )
                )
            })

            if (
                len(differential_terms)
                >= top_n
            ):
                break

        return {
            "positive_terms": positive_terms,
            "negative_terms": negative_terms,
            "differential_terms": (
                differential_terms
            ),
            "warning": (
                "Las contribuciones describen "
                "el comportamiento matemático "
                "del modelo, no causalidad."
            )
        }


    def predict(
        self,
        texts: str | Iterable[str],
        include_explanation: bool = False,
        explanation_top_n: int = 8,
        top_k: int | None = None
    ) -> dict[str, Any]:
        """Clasifica uno o varios documentos."""

        start_time = time.perf_counter()

        documents = self._prepare_inputs(
            texts
        )

        if not isinstance(
            include_explanation,
            bool
        ):

            raise TypeError(
                "include_explanation "
                "debe ser booleano."
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
            <= len(self.classes)
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

        results: list[dict[str, Any]] = []

        valid_positions: list[int] = []
        valid_texts: list[str] = []

        for index, value in enumerate(
            documents
        ):

            validation = self._validate_text(
                value
            )

            result = {
                "request_id": request_id,
                "record_id": int(index),
                "timestamp_utc": timestamp,
                "input_type": validation[
                    "input_type"
                ],
                "text": validation[
                    "text"
                ],
                "characters": int(
                    validation[
                        "characters"
                    ]
                ),
                "words": int(
                    validation[
                        "words"
                    ]
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
                "terminos_activos": 0,
                "accion_recomendada": (
                    "Corregir la entrada"
                ),
                "requiere_revision": True,
                "prediccion_utilizable": False,
                "advertencias": [],
                "ranking_categorias": None,
                "explicacion": None
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

        if valid_texts:

            matrix = (
                self.vectorizer
                .transform(
                    valid_texts
                )
                .tocsr()
            )

            scores = np.asarray(
                self.classifier
                .decision_function(
                    matrix
                )
            )

            if scores.ndim == 1:

                if len(self.classes) == 2:

                    scores = np.column_stack([
                        -scores,
                        scores
                    ])

                else:

                    scores = scores.reshape(
                        1,
                        -1
                    )

            active_term_counts = np.diff(
                matrix.indptr
            )

            for local_position, original_index in enumerate(
                valid_positions
            ):

                result = results[
                    original_index
                ]

                active_terms = int(
                    active_term_counts[
                        local_position
                    ]
                )

                result[
                    "terminos_activos"
                ] = active_terms

                if active_terms == 0:

                    result[
                        "validation_message"
                    ] = (
                        "El texto es válido, pero "
                        "no contiene términos reconocidos."
                    )

                    result[
                        "accion_recomendada"
                    ] = (
                        "Solicitar más contexto "
                        "o revisión humana"
                    )

                    result[
                        "advertencias"
                    ] = [
                        (
                            "No se devuelve una categoría "
                            "para evitar una predicción "
                            "basada únicamente en interceptos."
                        )
                    ]

                    continue

                document_scores = scores[
                    local_position
                ]

                ranking_indices = np.argsort(
                    document_scores
                )[::-1]

                predicted_index = int(
                    ranking_indices[0]
                )

                alternative_index = int(
                    ranking_indices[1]
                )

                predicted_score = float(
                    document_scores[
                        predicted_index
                    ]
                )

                alternative_score = float(
                    document_scores[
                        alternative_index
                    ]
                )

                margin = (
                    predicted_score
                    - alternative_score
                )

                level = self._margin_level(
                    margin
                )

                decision = (
                    self._operational_decision(
                        level=level,
                        active_terms=active_terms,
                        words=result[
                            "words"
                        ]
                    )
                )

                ranking = [
                    {
                        "position": int(
                            position
                        ),
                        "category": str(
                            self.classes[
                                class_index
                            ]
                        ),
                        "score": float(
                            document_scores[
                                class_index
                            ]
                        )
                    }
                    for position, class_index
                    in enumerate(
                        ranking_indices[
                            :top_k
                        ],
                        start=1
                    )
                ]

                result.update({
                    "validation_message": (
                        "Inferencia completada."
                    ),
                    "estado": decision[
                        "status"
                    ],
                    "categoria_predicha": str(
                        self.classes[
                            predicted_index
                        ]
                    ),
                    "segunda_categoria": str(
                        self.classes[
                            alternative_index
                        ]
                    ),
                    "puntuacion_ganadora": (
                        predicted_score
                    ),
                    "puntuacion_segunda": (
                        alternative_score
                    ),
                    "margen_decision": float(
                        margin
                    ),
                    "nivel_margen": level,
                    "accion_recomendada": (
                        decision[
                            "action"
                        ]
                    ),
                    "requiere_revision": bool(
                        decision[
                            "requires_review"
                        ]
                    ),
                    "prediccion_utilizable": bool(
                        decision[
                            "usable"
                        ]
                    ),
                    "advertencias": decision[
                        "warnings"
                    ],
                    "ranking_categorias": (
                        ranking
                    )
                })

                if include_explanation:

                    result[
                        "explicacion"
                    ] = self._explain_vector(
                        vector=matrix[
                            local_position
                        ],
                        predicted_index=(
                            predicted_index
                        ),
                        alternative_index=(
                            alternative_index
                        ),
                        top_n=int(
                            explanation_top_n
                        )
                    )

        duration = (
            time.perf_counter()
            - start_time
        )

        accepted = sum(
            result[
                "estado"
            ] == "aceptada"
            for result in results
        )

        review = sum(
            result[
                "estado"
            ] == "revision"
            for result in results
        )

        rejected = sum(
            result[
                "estado"
            ] == "rechazada"
            for result in results
        )

        return {
            "resumen": {
                "request_id": request_id,
                "timestamp_utc": timestamp,
                "interface_version": (
                    __version__
                ),
                "model_name": self.metadata.get(
                    "modelo"
                ),
                "documents_received": int(
                    len(documents)
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
                "duration_seconds": float(
                    duration
                ),
                "milliseconds_per_document": float(
                    duration
                    / len(documents)
                    * 1000
                ),
                "explanations_included": bool(
                    include_explanation
                ),
                "margin_is_probability": False
            },
            "resultados": results
        }
