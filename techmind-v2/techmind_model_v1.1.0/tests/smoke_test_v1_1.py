
from pathlib import Path
import sys

PACKAGE_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.insert(
    0,
    str(PACKAGE_ROOT),
)

from techmind import TechMindPredictor


def main():

    predictor = TechMindPredictor(
        package_root=PACKAGE_ROOT,
        verify_hash=True,
    )

    health = predictor.health()

    assert (
        health["interface_version"]
        == "1.0.0"
    )

    assert (
        health["model_version"]
        == "1.1.0"
    )

    assert (
        health["word_features"]
        == 30000
    )

    assert (
        health["char_features"]
        == 30000
    )

    assert (
        health["total_features"]
        == 60000
    )

    texts = [
        (
            "Este contenido explica cómo crear "
            "una API REST con Spring Boot y Java, "
            "incluyendo el uso de controladores, "
            "servicios y repositorios."
        ),

        (
            "Despliegue de contenedores Docker "
            "en Kubernetes sobre AWS."
        ),

        (
            "Entrenamiento de modelos de machine "
            "learning usando Python y scikit-learn."
        ),

        (
            "Interfaz web creada con React, "
            "JavaScript y componentes CSS."
        ),
    ]

    expected = [
        "backend",
        "cloud",
        "datascience",
        "frontend",
    ]

    response = predictor.predict(
        texts,
        include_explanation=True,
        explanation_top_n=5,
        top_k=4,
    )

    obtained = [
        item["categoria_predicha"]
        for item
        in response["resultados"]
    ]

    assert obtained == expected

    backend = response[
        "resultados"
    ][0]

    assert (
        backend[
            "categoria_predicha"
        ]
        == "backend"
    )

    assert (
        backend[
            "features_activas_total"
        ] > 0
    )

    assert (
        backend[
            "prediccion_utilizable"
        ]
    )

    print(
        "========================================"
    )
    print(
        "TECHMIND v1.1.0 — SMOKE TEST"
    )
    print(
        "========================================"
    )

    print(
        "Interface version:",
        health["interface_version"]
    )

    print(
        "Model version:",
        health["model_version"]
    )

    print(
        "Word features:",
        health["word_features"]
    )

    print(
        "Char features:",
        health["char_features"]
    )

    print(
        "Total features:",
        health["total_features"]
    )

    print(
        "Predicciones esperadas:",
        expected
    )

    print(
        "Predicciones obtenidas:",
        obtained
    )

    print(
        "\nSMOKE TEST: APROBADO"
    )


if __name__ == "__main__":
    main()
