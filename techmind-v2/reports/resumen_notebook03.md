# TechMind v2.0

## Resumen del Notebook 03

### Modelo definitivo

- **Modelo:** TF-IDF + SGDClassifier optimizado
- **Variante textual:** `texto_combinado_ponderado`
- **Clasificador:** `SGDClassifier`
- **Características TF-IDF:** 30,000
- **Registros de entrenamiento:** 3,666
- **Registros de prueba:** 917

### Resultados finales

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.8386 |
| Precision Macro | 0.8445 |
| Recall Macro | 0.8385 |
| F1 Macro | 0.8401 |
| F1 Weighted | 0.8397 |
| F1 Macro CV | 0.8432 |
| Diferencia test-CV | -0.0031 |

### Generalización

El resultado fue clasificado como **Generalización consistente**.
La diferencia entre validación cruzada y prueba fue de
`-0.0031`.

### Rendimiento por categoría

| Categoria   |   Precision |   Recall |     F1 |   Soporte |
|:------------|------------:|---------:|-------:|----------:|
| datascience |      0.9196 |   0.8318 | 0.8735 |       220 |
| cloud       |      0.8515 |   0.8405 | 0.846  |       232 |
| frontend    |      0.854  |   0.8283 | 0.841  |       233 |
| backend     |      0.7529 |   0.8534 | 0.8    |       232 |

### Comparación del modelo híbrido

El modelo textual obtuvo un F1 Macro de `0.8432`,
mientras que el modelo híbrido obtuvo `0.8282`.

La incorporación de las 19 características numéricas produjo una diferencia
de `-0.0150`. Por ello, se seleccionó el modelo
exclusivamente textual.

### Conclusión

El modelo definitivo superó las validaciones de reproducibilidad y evaluación.
El pipeline puede avanzar a la etapa de interpretabilidad, pruebas funcionales
y preparación para despliegue.

El conjunto de prueba no debe utilizarse para realizar nuevos ajustes de
hiperparámetros.
