from __future__ import annotations

import json
import os
import urllib.request

HOST = os.getenv(
    'TECHMIND_TEST_HOST',
    '127.0.0.1'
)

PORT = int(
    os.getenv(
        'TECHMIND_PORT',
        '8000'
    )
)

BASE_URL = f'http://{HOST}:{PORT}'

EXPECTED_SHA = (
    '1a495520f642416e7dd391f97417cd3d'
    '12dcd82ab11636b7f190e5ed6dafea61'
)


def get_json(path: str):
    with urllib.request.urlopen(
        BASE_URL + path,
        timeout=30
    ) as response:
        return (
            response.status,
            json.loads(
                response.read().decode('utf-8')
            )
        )


def post_json(path: str, payload: dict):
    body = json.dumps(
        payload,
        ensure_ascii=False
    ).encode('utf-8')

    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={
            'Content-Type':
                'application/json; charset=utf-8'
        },
        method='POST'
    )

    with urllib.request.urlopen(
        request,
        timeout=60
    ) as response:
        return (
            response.status,
            json.loads(
                response.read().decode('utf-8')
            )
        )


def main():
    print('=' * 70)
    print('TECHMIND v1.2 â€” DOCKER SMOKE TEST')
    print('=' * 70)

    status, health = get_json('/health')
    assert status == 200
    assert health['status'] == 'ok'
    assert health['model_loaded'] is True
    print('âœ… /health')

    status, info = get_json('/model-info')
    assert status == 200
    assert info['version'] == '1.2.0-multilingual'
    assert info['artifact_sha256'] == EXPECTED_SHA
    print('âœ… /model-info')
    print('âœ… SHA256')

    payload = {
        'texts': [
            (
                'Train a classification model '
                'and evaluate precision recall and F1.'
            ),
            (
                'Crear un endpoint REST con autenticaciÃ³n '
                'y acceso a base de datos.'
            ),
            (
                'ÐžÐ±ÑƒÑ‡Ð¸Ñ‚ÑŒ Ð¼Ð¾Ð´ÐµÐ»ÑŒ ÐºÐ»Ð°ÑÑÐ¸Ñ„Ð¸ÐºÐ°Ñ†Ð¸Ð¸ Ð¸ Ð¾Ñ†ÐµÐ½Ð¸Ñ‚ÑŒ '
                'precision recall Ð¸ F1.'
            ),
            (
                'Preparar una pizza con tomate y queso.'
            )
        ],
        'top_k': 4,
        'include_explanation': False
    }

    status, result = post_json(
        '/predict',
        payload
    )

    assert status == 200
    predictions = result['predictions']
    assert len(predictions) == 4

    assert predictions[0]['prediction'] == 'datascience'
    assert predictions[0]['decision'] != 'rejected_ood'

    assert predictions[1]['prediction'] == 'backend'
    assert predictions[1]['decision'] != 'rejected_ood'

    assert predictions[2]['prediction'] == 'datascience'
    assert predictions[2]['decision'] != 'rejected_ood'

    assert predictions[3]['decision'] == 'rejected_ood'

    print('âœ… /predict')
    print('âœ… English')
    print('âœ… EspaÃ±ol')
    print('âœ… Ð ÑƒÑÑÐºÐ¸Ð¹')
    print('âœ… OOD')

    print('\n' + '=' * 70)
    print('DOCKER SMOKE TEST PASSED')
    print('=' * 70)


if __name__ == '__main__':
    main()

