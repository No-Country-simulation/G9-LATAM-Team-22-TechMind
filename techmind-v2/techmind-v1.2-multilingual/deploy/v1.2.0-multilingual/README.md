# TechMind v1.2.0-multilingual — Deployment

## Estado

**validated_experimental_candidate**

Backend validado mediante:

- importación en proceso independiente
- carga independiente del predictor
- inferencia independiente
- FastAPI + Uvicorn
- `/health`
- `/model-info`
- `/predict`
- contrato OpenAPI
- verificación SHA-256

---

## Arquitectura

```text
Input
  |
  v
Input validation
  |
  v
MiniLM multilingual
  |
  v
Semantic domain support (5NN)
  |
  +-- similarity < 0.4266 --> rejected_ood
  |
  v
TF-IDF Word+Char + MiniLM
  |
  v
LinearSVC C=0.3
  |
  v
Decision margin
  |
  +-- margin < 0.8132 --> review
  |
  v
accepted
```

## Modelo

- Version: `1.2.0-multilingual`
- Status: `validated_experimental_candidate`
- Encoder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Embedding dimensions: `384`
- Classifier: `LinearSVC`
- C: `0.3`

## Controles operacionales

### Semantic domain support

- Métrica: `mean_cosine_similarity_5nn`
- Vecinos: `5`
- Threshold: `0.4266`

Si `similarity_5nn < 0.4266`, la entrada se marca como:

`rejected_ood`

### Decision margin

- Métrica: `top1_minus_top2_decision_margin`
- Threshold: `0.8132`

Si `margin < 0.8132`, la predicción se envía a:

`review`

En otro caso:

`accepted`

---

## Artefacto

Ruta:

```text
models/experimental/v1.2.0-multilingual/
techmind_hybrid_v1_2_0_multilingual.joblib
```

SHA-256:

```text
1a495520f642416e7dd391f97417cd3d12dcd82ab11636b7f190e5ed6dafea61
```

Este SHA identifica exactamente el artefacto validado.

---

## Configuración offline

Variables recomendadas:

```text
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
HF_HUB_DISABLE_TELEMETRY=1
TOKENIZERS_PARALLELISM=false
```

El predictor utiliza `local_files_only=True` para cargar MiniLM.

Por tanto, el encoder debe estar disponible previamente
en la caché local del servidor.

---

## Instalación

Desde la raíz del repositorio:

```bash
python -m pip install -r deploy/v1.2.0-multilingual/requirements-v1.2.txt
```

---

## Iniciar API

```bash
python deploy/v1.2.0-multilingual/start_server.py
```

Configuración por defecto:

```text
Host: 0.0.0.0
Port: 8000
```

Swagger:

`http://localhost:8000/docs`

---

## Endpoints

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`
- `/docs`
- `/redoc`
- `/openapi.json`

Estados operacionales posibles:

- `accepted`
- `review`
- `rejected_ood`
- `rejected_invalid`

Los scores de `LinearSVC` NO son probabilidades.

---

## Smoke test

Con la API ejecutándose:

```bash
python deploy/v1.2.0-multilingual/smoke_test_v12.py
```

Resultado esperado:

```text
DEPLOYMENT SMOKE TEST PASSED
```

---

## Validación del backend

```text
artifact_integrity             PASS
independent_import             PASS
independent_predictor_load     PASS
independent_inference          PASS
uvicorn_startup_health         PASS
http_model_info                PASS
http_predict                   PASS
openapi_contract               PASS
```

`BACKEND v1.2 READY FOR DEPLOYMENT: True`

---

## Benchmark final independiente

### v1.2

- Accuracy: `76.25%`
- F1 Macro: `75.70%`
- Cross-language consistency: `80.00%`

### Comparación con v1.1

| Métrica | v1.1 | v1.2 |
|---|---:|---:|
| Accuracy | 56.56% | 76.25% |
| F1 Macro | 57.05% | 75.70% |

Mejora absoluta:

- Accuracy: `+19.69 pp`
- F1 Macro: `+18.64 pp`

La comparación pareada mediante McNemar mostró una
diferencia estadísticamente significativa a favor de v1.2.

---

## Rendimiento por idioma

| Idioma | Accuracy |
|---|---:|
| EN | 77.50% |
| ES | 75.00% |
| ES/EN | 78.75% |
| RU | 73.75% |

---

## Rendimiento por categoría

| Categoría | Accuracy |
|---|---:|
| Backend | 90.00% |
| Cloud | 40.00% |
| Data Science | 83.75% |
| Frontend | 91.25% |

---

## Limitación conocida

La principal limitación identificada es `Cloud`.

Accuracy Cloud en el benchmark independiente: `40%`.

La mayoría de los errores Cloud fueron clasificados como Backend.

Esto sugiere una limitación de cobertura conceptual en la frontera:

`Cloud <-> Backend`

y no una degradación específica por idioma.

El modelo debe permanecer congelado para esta versión.

Las mejoras derivadas de este benchmark pertenecen a una versión
futura y deberán validarse mediante un nuevo holdout independiente.

---

## Estado de versiones

- `v1.1.0`: stable baseline / fallback
- `v1.2.0-multilingual`: validated experimental candidate
- Backend v1.2: ready for deployment
