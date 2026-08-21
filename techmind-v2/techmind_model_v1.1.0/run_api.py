"""Inicia la API local de TechMind."""

import os

import uvicorn


if __name__ == "__main__":
    host = os.getenv(
        "TECHMIND_API_HOST",
        "127.0.0.1"
    )

    port = int(
        os.getenv(
            "TECHMIND_API_PORT",
            "8000"
        )
    )

    uvicorn.run(
        "techmind_api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
