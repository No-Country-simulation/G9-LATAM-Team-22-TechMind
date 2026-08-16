# TechMind v1.2.0-multilingual — Artifact Certification

## Deployment artifact

File:

models/experimental/v1.2.0-multilingual/techmind_hybrid_v1_2_0_multilingual.joblib

Deployment SHA-256:

1a495520f642416e7dd391f97417cd3d12dcd82ab11636b7f190e5ed6dafea61

## Historical serialized artifact SHA-256

5f6ff8c4b350a9cbe8a9e7d531290bfda41a83d5337ae4174357ea170ea9dce3

The historical and deployment artifact files have different binary
SHA-256 values.

The current deployment artifact was functionally re-certified against
the frozen multilingual final benchmark before Docker packaging.

## Functional certification

Benchmark:

data/evaluation/multilingual_final_benchmark_v1.csv

Results:

- Documents: 320
- Correct: 244
- Accuracy: 0.7625
- F1 Macro: 0.756952
- Accepted: 120
- Review: 160
- Rejected OOD: 40
- Accepted errors: 10

Language accuracy:

- en: 0.7750
- es: 0.7500
- es_en: 0.7875
- ru: 0.7375

Category accuracy:

- backend: 0.9000
- cloud: 0.4000
- datascience: 0.8375
- frontend: 0.9125

Certification result:

FUNCTIONALLY MATCHES FROZEN v1.2: True

Model version:

1.2.0-multilingual

Status:

validated_experimental_candidate
