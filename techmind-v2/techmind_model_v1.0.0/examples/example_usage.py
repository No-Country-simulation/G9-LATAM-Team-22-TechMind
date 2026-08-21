"""Ejemplo básico de uso del paquete TechMind."""

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


predictor = TechMindPredictor(
    package_root=PACKAGE_ROOT
)


response = predictor.predict(
    [
        (
            "java spring boot rest api "
            "database backend"
        ),
        (
            "python pandas machine learning "
            "predictive model"
        )
    ],
    include_explanation=True,
    explanation_top_n=5
)


print(
    json.dumps(
        response,
        ensure_ascii=False,
        indent=4
    )
)
