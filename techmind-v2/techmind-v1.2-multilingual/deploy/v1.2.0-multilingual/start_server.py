\
from __future__ import annotations

import os

import uvicorn


def main() -> None:

    host = os.getenv(
        "TECHMIND_HOST",
        "0.0.0.0"
    )

    port = int(
        os.getenv(
            "TECHMIND_PORT",
            "8000"
        )
    )

    # Inferencia reproducible/offline.
    os.environ.setdefault(
        "HF_HUB_OFFLINE",
        "1"
    )

    os.environ.setdefault(
        "TRANSFORMERS_OFFLINE",
        "1"
    )

    os.environ.setdefault(
        "HF_HUB_DISABLE_TELEMETRY",
        "1"
    )

    os.environ.setdefault(
        "TOKENIZERS_PARALLELISM",
        "false"
    )

    uvicorn.run(
        "techmind_api_v12.main:app",
        host=host,
        port=port,
        workers=1,
        log_level="info",
    )


if __name__ == "__main__":
    main()
