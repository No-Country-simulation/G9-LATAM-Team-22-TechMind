"""Prueba independiente del paquete TechMind."""

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


from techmind import TechMindPredictor


TEXTS = ['java spring boot rest api microservices postgresql backend architecture', 'aws kubernetes terraform docker cloud infrastructure deployment', 'python pandas scikit-learn machine learning dataset predictive model', 'react javascript html css responsive frontend interface']

EXPECTED_PREDICTIONS = ['backend', 'cloud', 'datascience', 'frontend']


predictor = TechMindPredictor(
    package_root=PACKAGE_ROOT,
    verify_hash=True
)


health = predictor.health()

assert health["status"] == "ok"
assert health["tfidf_features"] == 30000
assert len(health["classes"]) == 4


response = predictor.predict(
    TEXTS,
    include_explanation=True,
    explanation_top_n=5
)

results = response["resultados"]

obtained_predictions = [
    record["categoria_predicha"]
    for record in results
]

assert obtained_predictions == EXPECTED_PREDICTIONS

assert all(
    record["prediccion_utilizable"]
    for record in results
)

assert all(
    record["terminos_activos"] > 0
    for record in results
)

assert all(
    record["margen_decision"] >= 0
    for record in results
)

assert all(
    isinstance(
        record["explicacion"],
        dict
    )
    for record in results
)


invalid_response = predictor.predict([
    "",
    None,
    12345,
    "zzzxqvvv pppqqqxxx"
])

invalid_results = (
    invalid_response[
        "resultados"
    ]
)

assert invalid_results[0]["estado"] == "rechazada"
assert invalid_results[1]["estado"] == "rechazada"
assert invalid_results[2]["estado"] == "rechazada"

assert (
    invalid_results[3]["estado"]
    == "rechazada"
)

assert (
    invalid_results[3]["categoria_predicha"]
    is None
)

assert (
    invalid_results[3]["terminos_activos"]
    == 0
)


output = {
    "status": "ok",
    "health": health,
    "expected_predictions": (
        EXPECTED_PREDICTIONS
    ),
    "obtained_predictions": (
        obtained_predictions
    ),
    "valid_documents": len(results),
    "invalid_documents": len(
        invalid_results
    ),
    "oov_rejected": True,
    "explanation_available": True
}


print(
    json.dumps(
        output,
        ensure_ascii=False
    )
)
