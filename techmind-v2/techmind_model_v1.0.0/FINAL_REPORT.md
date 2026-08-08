# TechMind v2.0 — Informe técnico final

## 1. Resumen ejecutivo

TechMind es una solución de procesamiento de lenguaje natural diseñada para
clasificar contenido tecnológico en cuatro categorías:

- backend
- cloud
- datascience
- frontend

El modelo final utiliza TF-IDF y un SGDClassifier optimizado. La variante
textual seleccionada fue `texto_combinado_ponderado`.

## 2. Preparación de datos

| Indicador | Resultado |
|---|---:|
| Registros originales | 5,000 |
| Registros finales | 4,583 |
| Registros de entrenamiento | 3,666 |
| Registros de prueba | 917 |
| Ratio de balance | 0.946 |
| Variables numéricas generadas | 21 |
| Variables numéricas utilizadas | 19 |

La preparación eliminó textos duplicados, conflictos de categoría y registros
redundantes. El conjunto final no contiene documentos vacíos, valores nulos,
valores infinitos ni conflictos textuales residuales.

## 3. Selección del modelo

Se evaluaron distintas variantes textuales y algoritmos de clasificación.

La mejor combinación fue:

```text
Variante: texto_combinado_ponderado
Vectorización: TF-IDF
Clasificador: SGDClassifier optimizado
Características TF-IDF: 30,000
```

## 4. Resultados finales

| Métrica | Resultado |
|---|---:|
| Accuracy Test | 0.8386 |
| Precision Macro Test | 0.8445 |
| Recall Macro Test | 0.8385 |
| F1 Macro Test | 0.8401 |
| F1 Weighted Test | 0.8397 |
| F1 Macro CV | 0.8432 |
| Diferencia Test-CV | -0.0031 |

La diferencia entre test y validación cruzada fue pequeña, lo que indica una
generalización consistente.

La categoría con mejor rendimiento fue `datascience` con un F1 de
0.8735. La categoría más difícil fue
`backend` con un F1 de
0.8000.

## 5. Explicabilidad

El paquete incluye:

- Importancia global de términos.
- Explicaciones locales por documento.
- Contribuciones positivas y negativas.
- Ranking de categorías.
- Análisis de términos ambiguos y ruido.
- Auditoría de predicciones incorrectas.

## 6. Incertidumbre y revisión humana

TechMind utiliza el margen entre las dos categorías con mayor puntuación para
identificar predicciones ambiguas.

Este margen no representa una probabilidad calibrada.

Las predicciones con margen reducido, pocos términos reconocidos o contenido
fuera del vocabulario pueden ser rechazadas o enviadas a revisión.

## 7. Robustez

El modelo fue evaluado con:

- Textos breves.
- Entradas fuera del vocabulario.
- Contenido multitemático.
- Ruido textual.
- Variaciones controladas.
- Casos representativos del conjunto reservado.

## 8. Paquete de inferencia

El paquete exportado incluye una clase `TechMindPredictor` con:

- Verificación SHA-256 del modelo.
- Inferencia individual y por lotes.
- Validación de entradas.
- Rechazo de contenido OOV.
- Ranking de categorías.
- Explicaciones opcionales.
- Health check.

El smoke test independiente fue aprobado.

## 9. API REST

La API FastAPI expone:

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /docs`
- `GET /redoc`
- `GET /openapi.json`

Las solicitudes incorrectas son rechazadas mediante validaciones Pydantic.

## 10. Contenedorización

El paquete incluye:

- Dockerfile.
- Docker Compose.
- Health check.
- Usuario sin privilegios.
- Sistema de archivos de solo lectura en Compose.
- Eliminación de capacidades Linux.
- Restricción del puerto a `127.0.0.1`.

No disponible en el entorno actual; la configuración fue validada estáticamente.

## 11. Monitoreo

El perfil de referencia utiliza 917 documentos.

Las métricas supervisadas incluyen:

- Tasa de aceptación.
- Tasa de revisión.
- Tasa de rechazo.
- Tasa OOV.
- Márgenes bajos.
- Términos reconocidos.
- Longitud del texto.
- Distribución de categorías.
- Distribución de estados.

Las señales de cambio utilizan PSI y divergencia Jensen-Shannon.

Estas señales no sustituyen una evaluación con etiquetas reales.

## 12. Auditoría

| Indicador | Resultado |
|---|---:|
| Controles aprobados | 14/14 |
| Componentes aprobados | 16/16 |
| Integridad del modelo | True |
| SHA-256 del modelo | `488ec7d47f7697f870fde6877d8df54e5ce1fedbc29842dd669a1014c7715cfb` |

## 13. Limitaciones principales

- El modelo solo reconoce cuatro categorías.
- El margen no está calibrado como probabilidad.
- Backend presenta el F1 más bajo.
- Textos muy cortos o multitemáticos son más difíciles.
- Los términos tecnológicos nuevos pueden quedar fuera del vocabulario.
- La API no debe exponerse públicamente sin autenticación y HTTPS.
- La validación real de Docker está pendiente.
- El monitoreo sin etiquetas no mide directamente la calidad real.

## 14. Recomendaciones principales

1. Construir y probar la imagen Docker.
2. Añadir autenticación, HTTPS y límites de solicitudes.
3. Reforzar la categoría backend.
4. Recolectar etiquetas reales de producción.
5. Calibrar las puntuaciones del modelo.
6. Ajustar los umbrales de monitoreo.
7. Aplicar anonimización y retención de registros.
8. Comparar el modelo con embeddings o transformers.
9. Evaluar clasificación multietiqueta.
10. Automatizar pruebas y despliegues mediante CI/CD.

## 15. Conclusión

TechMind v2.0 completó satisfactoriamente el ciclo técnico de preparación de
datos, modelado, evaluación, explicabilidad, empaquetado, API, configuración de
despliegue y monitoreo.

El modelo alcanzó un F1 Macro Test de 0.8401 y mantuvo una
diferencia Test-CV de -0.0031.

El entregable es reproducible, auditable y está preparado para pruebas de
despliegue en un entorno con Docker disponible.
