"""Smoke test independiente de la API TechMind."""

import json
import sys

from pathlib import Path


PACKAGE_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.insert(
    0,
    str(PACKAGE_ROOT)
)


from fastapi.testclient import TestClient
from techmind_api.main import app


TEST_CASES_PATH = (
    PACKAGE_ROOT
    / "api_test_cases.json"
)


with TEST_CASES_PATH.open(
    "r",
    encoding="utf-8"
) as file:

    test_cases = json.load(
        file
    )


with TestClient(app) as client:

    root_response = client.get(
        "/"
    )

    health_response = client.get(
        "/health"
    )

    model_info_response = client.get(
        "/model-info"
    )

    prediction_response = client.post(
        "/predict",
        json={
            "textos": test_cases[
                "valid_texts"
            ],
            "incluir_explicacion": True,
            "top_n_explicacion": 5,
            "top_k": 4
        }
    )

    oov_response = client.post(
        "/predict",
        json={
            "textos": [
                test_cases[
                    "oov_text"
                ]
            ]
        }
    )

    invalid_response = client.post(
        "/predict",
        json={
            "textos": []
        }
    )

    docs_response = client.get(
        "/docs"
    )

    openapi_response = client.get(
        "/openapi.json"
    )


assert root_response.status_code == 200
assert health_response.status_code == 200
assert model_info_response.status_code == 200
assert prediction_response.status_code == 200
assert oov_response.status_code == 200
assert invalid_response.status_code == 422
assert docs_response.status_code == 200
assert openapi_response.status_code == 200


health = health_response.json()

assert health["status"] == "ok"
assert health["ready"] is True

assert (
    health["tfidf_features"]
    ==
    test_cases[
        "expected_tfidf_features"
    ]
)

assert (
    health["classes"]
    ==
    test_cases[
        "expected_classes"
    ]
)


prediction_data = (
    prediction_response.json()
)

obtained_predictions = [
    record[
        "categoria_predicha"
    ]
    for record in (
        prediction_data[
            "resultados"
        ]
    )
]

assert (
    obtained_predictions
    ==
    test_cases[
        "expected_predictions"
    ]
)


oov_record = (
    oov_response
    .json()[
        "resultados"
    ][0]
)

assert (
    oov_record["estado"]
    ==
    "rechazada"
)

assert (
    oov_record[
        "categoria_predicha"
    ]
    is None
)

assert (
    oov_record[
        "terminos_activos"
    ]
    == 0
)


openapi_paths = set(
    openapi_response
    .json()[
        "paths"
    ].keys()
)

assert {
    "/health",
    "/model-info",
    "/predict"
}.issubset(
    openapi_paths
)


output = {
    "status": "ok",
    "health_status": (
        health_response.status_code
    ),
    "prediction_status": (
        prediction_response.status_code
    ),
    "expected_predictions": (
        test_cases[
            "expected_predictions"
        ]
    ),
    "obtained_predictions": (
        obtained_predictions
    ),
    "oov_rejected": True,
    "validation_422": True,
    "documentation_available": True,
    "routes": sorted(
        openapi_paths
    )
}


print(
    json.dumps(
        output,
        ensure_ascii=False
    )
)
