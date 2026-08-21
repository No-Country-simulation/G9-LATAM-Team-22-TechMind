\
from __future__ import annotations

import json
import os
import urllib.request


HOST = os.getenv(
    "TECHMIND_TEST_HOST",
    "127.0.0.1"
)

PORT = int(
    os.getenv(
        "TECHMIND_PORT",
        "8000"
    )
)

BASE_URL = (
    f"http://{HOST}:{PORT}"
)


def get_json(path: str):

    with urllib.request.urlopen(
        BASE_URL + path,
        timeout=15
    ) as response:

        return (
            response.status,
            json.loads(
                response
                .read()
                .decode("utf-8")
            )
        )


def post_json(
    path: str,
    payload: dict
):

    body = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={
            "Content-Type":
                "application/json; charset=utf-8"
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return (
            response.status,
            json.loads(
                response
                .read()
                .decode("utf-8")
            )
        )


def main() -> None:

    print("=" * 70)
    print("TECHMIND v1.2 — DEPLOYMENT SMOKE TEST")
    print("=" * 70)

    health_status, health = get_json(
        "/health"
    )

    print(
        "\n/health:",
        health_status,
        health
    )

    assert health_status == 200
    assert health["status"] == "ok"
    assert health["model_loaded"] is True

    info_status, info = get_json(
        "/model-info"
    )

    print(
        "\n/model-info:",
        info_status
    )

    print(
        "Version:",
        info["version"]
    )

    print(
        "SHA:",
        info["artifact_sha256"]
    )

    assert info_status == 200

    assert (
        info["version"]
        ==
        "1.2.0-multilingual"
    )

    predict_status, result = post_json(
        "/predict",
        {
            "texts": [
                (
                    "Train a classification model "
                    "and evaluate precision recall "
                    "and F1."
                ),
                (
                    "Preparar una pizza con "
                    "tomate y queso."
                )
            ],
            "top_k": 4
        }
    )

    print(
        "\n/predict:",
        predict_status
    )

    for item in result["predictions"]:

        print(
            item["prediction"],
            "→",
            item["decision"]
        )

    assert predict_status == 200

    assert (
        result["predictions"][0][
            "decision"
        ]
        != "rejected_ood"
    )

    assert (
        result["predictions"][1][
            "decision"
        ]
        == "rejected_ood"
    )

    print(
        "\n✅ DEPLOYMENT SMOKE TEST PASSED"
    )


if __name__ == "__main__":
    main()
