# TechMind Model Package

Paquete independiente de inferencia para el modelo final de
TechMind v2.0.

## Modelo

- **Modelo:** TF-IDF + SGDClassifier optimizado
- **Versión:** 1.0.0
- **Categorías:** backend, cloud, datascience, frontend
- **Características TF-IDF:** 30,000
- **F1 Macro final:** 0.8401
- **Accuracy final:** 0.8386

## Estructura

```text
techmind_model/
├── techmind/
│   ├── __init__.py
│   └── predictor.py
├── artifacts/
│   ├── techmind_modelo_final.joblib
│   ├── techmind_modelo_final_metadata.json
│   ├── configuracion_inferencia.json
│   └── contrato_inferencia.json
├── examples/
│   └── example_usage.py
├── tests/
│   └── smoke_test.py
├── reports/
│   └── smoke_test_result.json
├── README.md
├── requirements.txt
├── runtime.json
├── package_metadata.json
├── manifest.json
└── VERSION
```

## Instalación de dependencias

```bash
python -m pip install -r requirements.txt
```

## Uso básico

```python
from techmind import TechMindPredictor

predictor = TechMindPredictor(
    package_root="ruta/al/paquete"
)

response = predictor.predict(
    "python pandas machine learning predictive model"
)

print(response)
```

## Inferencia con explicación

```python
response = predictor.predict(
    [
        "aws kubernetes terraform cloud infrastructure",
        "react javascript css frontend interface"
    ],
    include_explanation=True,
    explanation_top_n=5
)
```

## Verificar el estado del modelo

```python
health = predictor.health()

print(health)
```

## Prueba técnica

Desde el directorio raíz del paquete:

```bash
python tests/smoke_test.py
```

## Respuesta principal

La función `predict()` devuelve una estructura con:

- Estado de la entrada.
- Categoría predicha.
- Segunda categoría.
- Puntuaciones de decisión.
- Margen de decisión.
- Nivel descriptivo del margen.
- Cantidad de términos activos.
- Acción operativa recomendada.
- Ranking de categorías.
- Explicación local opcional.

## Consideraciones operativas

El margen de decisión no es una probabilidad calibrada.

Los textos vacíos, inválidos o sin términos reconocidos se rechazan.
Los documentos con margen bajo, muy pocas palabras o cobertura reducida
del vocabulario se marcan para revisión.

Los umbrales incluidos son descriptivos y deben validarse nuevamente
con datos etiquetados de producción.

## Integridad

SHA-256 del modelo:

```text
488ec7d47f7697f870fde6877d8df54e5ce1fedbc29842dd669a1014c7715cfb
```

## Restricciones

- No utilizar el margen como porcentaje de confianza.
- No aceptar automáticamente entradas sin vocabulario reconocido.
- No modificar directamente el archivo del modelo.
- No reajustar umbrales con el conjunto de prueba original.

<!-- TECHMIND_API_START -->

## API REST local

El paquete incluye una API local construida con FastAPI.

### Instalar dependencias

```bash
python -m pip install -r requirements-api.txt
```

### Iniciar la API

```bash
python run_api.py
```

La API se inicia por defecto en:

```text
http://127.0.0.1:8000
```

Documentación interactiva:

```text
http://127.0.0.1:8000/docs
```

### Endpoints

- `GET /health`: estado del modelo y de la API.
- `GET /model-info`: información técnica del modelo.
- `POST /predict`: clasificación individual o por lotes.
- `GET /docs`: documentación Swagger.
- `GET /redoc`: documentación ReDoc.

### Ejemplo de solicitud

```json
{
    "textos": [
        "python pandas machine learning predictive model",
        "react javascript css frontend interface"
    ],
    "incluir_explicacion": true,
    "top_n_explicacion": 5,
    "top_k": 4
}
```

El margen de decisión no representa una probabilidad calibrada.

<!-- TECHMIND_API_END -->

<!-- TECHMIND_DOCKER_START -->

## Ejecución con Docker

Construir la imagen:

```bash
docker build -t techmind-api:1.0.0 .
```

Ejecutar la API local:

```bash
docker run --rm \
  --name techmind-api \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -p 127.0.0.1:8000:8000 \
  techmind-api:1.0.0
```

Mediante Docker Compose:

```bash
docker compose up --build
```

Documentación local:

```text
http://127.0.0.1:8000/docs
```

La guía completa se encuentra en `DEPLOYMENT.md`.

<!-- TECHMIND_DOCKER_END -->

<!-- TECHMIND_MONITORING_START -->

## Monitoreo operativo

El paquete incluye un perfil de referencia y registros para supervisar:

- Predicciones aceptadas.
- Predicciones enviadas a revisión.
- Entradas rechazadas.
- Contenido fuera del vocabulario.
- Márgenes de decisión.
- Distribución de categorías.
- Cambios estadísticos mediante PSI y Jensen-Shannon.

La documentación completa se encuentra en `MONITORING.md`.

Las señales estadísticas no sustituyen la evaluación con etiquetas reales.

<!-- TECHMIND_MONITORING_END -->

<!-- TECHMIND_FINAL_REPORT_START -->

## Estado final del proyecto

TechMind v2.0 completó el ciclo de preparación de datos, modelado, evaluación,
explicabilidad, empaquetado, API REST, configuración Docker y monitoreo.

| Indicador | Resultado |
|---|---:|
| Registros finales | 4,583 |
| F1 Macro CV | 0.8432 |
| F1 Macro Test | 0.8401 |
| Accuracy Test | 0.8386 |
| Características TF-IDF | 30,000 |
| Componentes aprobados | 16/16 |

El informe técnico completo se encuentra en `FINAL_REPORT.md`.

<!-- TECHMIND_FINAL_REPORT_END -->
