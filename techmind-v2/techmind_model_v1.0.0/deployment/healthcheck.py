"""Health check interno del contenedor TechMind."""

import json
import sys
import urllib.error
import urllib.request


HEALTH_URL = (
    "http://127.0.0.1:8000/health"
)


def main() -> int:
    try:
        request = urllib.request.Request(
            HEALTH_URL,
            method="GET",
            headers={
                "Accept": "application/json"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:

            status_code = int(
                response.status
            )

            payload = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        healthy = bool(
            status_code == 200
            and
            payload.get("status") == "ok"
            and
            payload.get("ready") is True
        )

        return 0 if healthy else 1

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        OSError
    ):
        return 1


if __name__ == "__main__":
    sys.exit(
        main()
    )
