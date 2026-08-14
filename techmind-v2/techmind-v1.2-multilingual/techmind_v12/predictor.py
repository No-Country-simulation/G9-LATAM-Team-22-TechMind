\
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any
import hashlib

import joblib
import numpy as np

from scipy.sparse import (
    csr_matrix,
    hstack,
)

from sklearn.neighbors import NearestNeighbors

from sentence_transformers import SentenceTransformer


class TechMindPredictor:
    """
    Predictor experimental para TechMind v1.2.0-multilingual.

    Arquitectura
    ------------
    TF-IDF Word+Char
        +
    paraphrase-multilingual-MiniLM-L12-v2
        +
    LinearSVC

    Controles operacionales
    -----------------------
    1. Validación de entrada.
    2. Semantic domain-support mediante similitud media 5NN.
    3. Clasificación híbrida.
    4. Revisión por margen top1 - top2.

    Nota
    ----
    Los scores de LinearSVC NO son probabilidades.
    """

    def __init__(
        self,
        model_path: str | Path,
    ) -> None:

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"No existe el artefacto: {self.model_path}"
            )

        # -----------------------------------------------------
        # CARGA DEL ARTEFACTO
        # -----------------------------------------------------

        artifact = joblib.load(
            self.model_path
        )

        self.artifact = artifact

        self.version = artifact[
            "version"
        ]

        self.status = artifact.get(
            "status",
            "experimental"
        )

        self.features = artifact[
            "features"
        ]

        self.classifier = artifact[
            "classifier"
        ]

        self.classes_ = np.asarray(
            artifact.get(
                "classes",
                self.classifier.classes_
            )
        )

        # -----------------------------------------------------
        # EMBEDDING MODEL
        # -----------------------------------------------------

        self.embedding_model_name = (
            artifact[
                "embedding_model"
            ]
        )

        self.embedding_dimension = int(
            artifact[
                "embedding_dimension"
            ]
        )

        self.normalize_embeddings = bool(
            artifact.get(
                "normalize_embeddings",
                True
            )
        )

        self.encoder = SentenceTransformer(
            self.embedding_model_name,
            local_files_only=True
        )

        # -----------------------------------------------------
        # DOMAIN SUPPORT
        # -----------------------------------------------------

        self.domain_reference_embeddings = (
            np.asarray(
                artifact[
                    "domain_reference_embeddings"
                ],
                dtype=np.float32
            )
        )

        domain_control = artifact[
            "domain_control"
        ]

        self.domain_n_neighbors = int(
            domain_control[
                "n_neighbors"
            ]
        )

        self.domain_threshold = float(
            domain_control[
                "threshold"
            ]
        )

        self.domain_index = (
            NearestNeighbors(
                n_neighbors=(
                    self.domain_n_neighbors
                ),
                metric="cosine",
                algorithm="brute",
                n_jobs=1
            )
        )

        self.domain_index.fit(
            self.domain_reference_embeddings
        )

        # -----------------------------------------------------
        # CONFIDENCE CONTROL
        # -----------------------------------------------------

        confidence_control = artifact[
            "confidence_control"
        ]

        self.margin_threshold = float(
            confidence_control[
                "threshold"
            ]
        )

        # -----------------------------------------------------
        # INTEGRITY
        # -----------------------------------------------------

        self.artifact_sha256 = (
            self._sha256_file(
                self.model_path
            )
        )


    # =========================================================
    # PUBLIC INFO
    # =========================================================

    def model_info(
        self
    ) -> dict[str, Any]:

        return {

            "version":
                self.version,

            "status":
                self.status,

            "architecture":
                self.artifact.get(
                    "architecture"
                ),

            "classifier":
                self.artifact.get(
                    "classifier_type",
                    type(
                        self.classifier
                    ).__name__
                ),

            "classifier_C":
                self.artifact.get(
                    "classifier_C"
                ),

            "embedding_model":
                self.embedding_model_name,

            "embedding_dimension":
                self.embedding_dimension,

            "classes":
                self.classes_.tolist(),

            "domain_control": {
                "metric":
                    "mean_cosine_similarity_5nn",

                "threshold":
                    self.domain_threshold,

                "n_neighbors":
                    self.domain_n_neighbors,
            },

            "confidence_control": {
                "metric":
                    "top1_minus_top2_decision_margin",

                "threshold":
                    self.margin_threshold,
            },

            "artifact_sha256":
                self.artifact_sha256,

            "scores_are_probabilities":
                False,
        }


    # =========================================================
    # PREDICT
    # =========================================================

    def predict(
        self,
        texts: str | Iterable[str],
        include_explanation: bool = False,
        explanation_top_n: int = 8,
        top_k: int | None = None,
    ) -> dict[str, Any]:

        # -----------------------------------------------------
        # NORMALIZACIÓN DE ENTRADA
        # -----------------------------------------------------

        original_inputs = (
            self._normalize_input(
                texts
            )
        )

        if explanation_top_n <= 0:
            raise ValueError(
                "explanation_top_n debe ser > 0."
            )

        if top_k is not None:

            if (
                not isinstance(
                    top_k,
                    int
                )
                or top_k <= 0
            ):
                raise ValueError(
                    "top_k debe ser un entero > 0."
                )

            top_k = min(
                top_k,
                len(
                    self.classes_
                )
            )

        # -----------------------------------------------------
        # VALIDACIÓN
        # -----------------------------------------------------

        valid_mask = np.array(
            [
                self._is_valid_text(
                    value
                )
                for value
                in original_inputs
            ],
            dtype=bool
        )

        results: list[
            dict[str, Any] | None
        ] = [
            None
        ] * len(
            original_inputs
        )

        # Entradas inválidas no pasan por el modelo.
        for idx, is_valid in enumerate(
            valid_mask
        ):

            if not is_valid:

                results[idx] = {
                    "index":
                        idx,

                    "text":
                        original_inputs[
                            idx
                        ],

                    "valid_input":
                        False,

                    "decision":
                        "rejected_invalid",

                    "prediction":
                        None,

                    "second_category":
                        None,

                    "decision_margin":
                        None,

                    "domain_similarity_5nn":
                        None,

                    "tfidf_active_features":
                        0,

                    "reason":
                        "invalid_input",
                }

        valid_indices = np.flatnonzero(
            valid_mask
        )

        if len(
            valid_indices
        ) == 0:

            return self._build_response(
                results
            )

        valid_texts = [
            original_inputs[i]
            for i
            in valid_indices
        ]

        # -----------------------------------------------------
        # MINILM
        # -----------------------------------------------------

        embeddings = (
            self.encoder.encode(
                valid_texts,
                batch_size=32,
                normalize_embeddings=(
                    self.normalize_embeddings
                ),
                convert_to_numpy=True,
                show_progress_bar=False
            )
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        # -----------------------------------------------------
        # SEMANTIC DOMAIN SUPPORT
        # -----------------------------------------------------

        domain_distances, _ = (
            self.domain_index.kneighbors(
                embeddings
            )
        )

        domain_similarities = (
            1.0
            -
            domain_distances
        )

        domain_similarity_5nn = (
            domain_similarities.mean(
                axis=1
            )
        )

        # -----------------------------------------------------
        # TF-IDF
        # -----------------------------------------------------

        tfidf = (
            self.features.transform(
                valid_texts
            )
        )

        tfidf_active = np.asarray(
            tfidf.getnnz(
                axis=1
            )
        ).ravel()

        # -----------------------------------------------------
        # HYBRID REPRESENTATION
        # -----------------------------------------------------

        hybrid = hstack(
            [
                tfidf,
                csr_matrix(
                    embeddings
                )
            ],
            format="csr"
        )

        if (
            hybrid.shape[1]
            !=
            self.classifier.n_features_in_
        ):
            raise RuntimeError(
                "Dimensión híbrida incompatible "
                "con el clasificador."
            )

        # -----------------------------------------------------
        # LINEARSVC SCORES
        # -----------------------------------------------------

        scores = (
            self.classifier
            .decision_function(
                hybrid
            )
        )

        scores = np.asarray(
            scores
        )

        if scores.ndim != 2:
            raise RuntimeError(
                "Se esperaba clasificación "
                "multiclase con decision_function 2D."
            )

        order = np.argsort(
            scores,
            axis=1
        )

        top1_idx = order[
            :,
            -1
        ]

        top2_idx = order[
            :,
            -2
        ]

        top1_scores = scores[
            np.arange(
                len(valid_texts)
            ),
            top1_idx
        ]

        top2_scores = scores[
            np.arange(
                len(valid_texts)
            ),
            top2_idx
        ]

        margins = (
            top1_scores
            -
            top2_scores
        )

        predicted_classes = (
            self.classes_[
                top1_idx
            ]
        )

        second_classes = (
            self.classes_[
                top2_idx
            ]
        )

        # -----------------------------------------------------
        # RESULTS
        # -----------------------------------------------------

        for local_idx, original_idx in enumerate(
            valid_indices
        ):

            similarity = float(
                domain_similarity_5nn[
                    local_idx
                ]
            )

            margin = float(
                margins[
                    local_idx
                ]
            )

            predicted = str(
                predicted_classes[
                    local_idx
                ]
            )

            second = str(
                second_classes[
                    local_idx
                ]
            )

            # Orden operacional:
            #
            # valid input
            # -> semantic support
            # -> margin
            #
            if (
                similarity
                <
                self.domain_threshold
            ):

                decision = (
                    "rejected_ood"
                )

                reason = (
                    "low_semantic_domain_support"
                )

            elif (
                margin
                <
                self.margin_threshold
            ):

                decision = (
                    "review"
                )

                reason = (
                    "low_decision_margin"
                )

            else:

                decision = (
                    "accepted"
                )

                reason = None

            item = {

                "index":
                    int(
                        original_idx
                    ),

                "text":
                    original_inputs[
                        original_idx
                    ],

                "valid_input":
                    True,

                "decision":
                    decision,

                "prediction":
                    predicted,

                "second_category":
                    second,

                "decision_margin":
                    margin,

                "domain_similarity_5nn":
                    similarity,

                "tfidf_active_features":
                    int(
                        tfidf_active[
                            local_idx
                        ]
                    ),

                "reason":
                    reason,

                "score_top1":
                    float(
                        top1_scores[
                            local_idx
                        ]
                    ),

                "score_top2":
                    float(
                        top2_scores[
                            local_idx
                        ]
                    ),
            }

            # -------------------------------------------------
            # TOP-K
            # -------------------------------------------------

            if top_k is not None:

                ranking_idx = (
                    order[
                        local_idx
                    ][::-1][
                        :top_k
                    ]
                )

                item[
                    "top_k"
                ] = [

                    {
                        "category":
                            str(
                                self.classes_[
                                    class_idx
                                ]
                            ),

                        "score":
                            float(
                                scores[
                                    local_idx,
                                    class_idx
                                ]
                            )
                    }

                    for class_idx
                    in ranking_idx
                ]

            # -------------------------------------------------
            # EXPLANATION
            # -------------------------------------------------

            if include_explanation:

                item[
                    "explanation"
                ] = (
                    self._explain_tfidf(
                        tfidf_row=(
                            tfidf[
                                local_idx
                            ]
                        ),
                        predicted_idx=int(
                            top1_idx[
                                local_idx
                            ]
                        ),
                        second_idx=int(
                            top2_idx[
                                local_idx
                            ]
                        ),
                        top_n=(
                            explanation_top_n
                        )
                    )
                )

            results[
                original_idx
            ] = item

        return self._build_response(
            results
        )


    # =========================================================
    # EXPLAINABILITY
    # =========================================================

    def _explain_tfidf(
        self,
        tfidf_row,
        predicted_idx: int,
        second_idx: int,
        top_n: int,
    ) -> dict[str, Any]:

        """
        Explicación local aproximada limitada al componente
        interpretable TF-IDF.

        NO es una explicación causal del modelo completo.
        """

        tfidf_dim = (
            tfidf_row.shape[1]
        )

        coef = np.asarray(
            self.classifier.coef_
        )

        if (
            coef.shape[1]
            <
            tfidf_dim
        ):
            return {
                "available":
                    False,

                "reason":
                    "classifier_dimension_mismatch",
            }

        differential_coef = (
            coef[
                predicted_idx,
                :tfidf_dim
            ]
            -
            coef[
                second_idx,
                :tfidf_dim
            ]
        )

        row = (
            tfidf_row
            .tocsr()
        )

        active_indices = (
            row.indices
        )

        active_values = (
            row.data
        )

        if len(
            active_indices
        ) == 0:

            return {
                "available":
                    True,

                "scope":
                    "tfidf_differential_only",

                "terms":
                    [],
            }

        contributions = (
            active_values
            *
            differential_coef[
                active_indices
            ]
        )

        order = np.argsort(
            np.abs(
                contributions
            )
        )[::-1][
            :top_n
        ]

        feature_names = (
            self._feature_names(
                tfidf_dim
            )
        )

        terms = []

        for pos in order:

            feature_idx = int(
                active_indices[
                    pos
                ]
            )

            contribution = float(
                contributions[
                    pos
                ]
            )

            terms.append({
                "feature":
                    feature_names[
                        feature_idx
                    ],

                "value":
                    float(
                        active_values[
                            pos
                        ]
                    ),

                "differential_contribution":
                    contribution,

                "direction":
                    (
                        "predicted"
                        if contribution >= 0
                        else "second_category"
                    )
            })

        return {
            "available":
                True,

            "scope":
                "tfidf_differential_only",

            "note":
                (
                    "MiniLM dimensions are not mapped "
                    "to human-readable terms."
                ),

            "terms":
                terms,
        }


    # =========================================================
    # HELPERS
    # =========================================================

    def _feature_names(
        self,
        tfidf_dim: int,
    ) -> list[str]:

        try:

            names = (
                self.features
                .get_feature_names_out()
            )

            names = [
                str(x)
                for x
                in names
            ]

            if (
                len(names)
                ==
                tfidf_dim
            ):
                return names

        except Exception:
            pass

        return [
            f"feature_{i}"
            for i
            in range(
                tfidf_dim
            )
        ]


    @staticmethod
    def _normalize_input(
        texts: str | Iterable[str],
    ) -> list[Any]:

        if isinstance(
            texts,
            str
        ):
            return [
                texts
            ]

        if texts is None:
            return [
                None
            ]

        try:
            return list(
                texts
            )

        except TypeError as exc:

            raise TypeError(
                "texts debe ser str "
                "o Iterable[str]."
            ) from exc


    @staticmethod
    def _is_valid_text(
        value: Any,
    ) -> bool:

        return (
            isinstance(
                value,
                str
            )
            and bool(
                value.strip()
            )
        )


    def _build_response(
        self,
        results: list[
            dict[str, Any] | None
        ],
    ) -> dict[str, Any]:

        final_results = [
            x
            for x
            in results
            if x is not None
        ]

        decisions = {
            "accepted": 0,
            "review": 0,
            "rejected_ood": 0,
            "rejected_invalid": 0,
        }

        for item in final_results:

            decision = item[
                "decision"
            ]

            decisions[
                decision
            ] = (
                decisions.get(
                    decision,
                    0
                )
                +
                1
            )

        return {

            "model_version":
                self.version,

            "model_status":
                self.status,

            "n_inputs":
                len(
                    final_results
                ),

            "summary":
                decisions,

            "predictions":
                final_results,
        }


    @staticmethod
    def _sha256_file(
        path: Path,
    ) -> str:

        sha256 = hashlib.sha256()

        with path.open(
            "rb"
        ) as f:

            for block in iter(
                lambda: f.read(
                    1024 * 1024
                ),
                b""
            ):
                sha256.update(
                    block
                )

        return (
            sha256.hexdigest()
        )
