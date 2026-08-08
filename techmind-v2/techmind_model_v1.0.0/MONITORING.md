# Monitoreo operativo de TechMind

El paquete incluye un perfil de referencia y funciones para supervisar
lotes de predicciones.

## Métricas registradas

- Volumen de documentos.
- Tasa de aceptación.
- Tasa de revisión.
- Tasa de rechazo.
- Tasa de documentos fuera del vocabulario.
- Proporción de márgenes bajos.
- Cantidad media de términos reconocidos.
- Longitud media del texto.
- Distribución de categorías.
- Distribución de estados.

## Señales estadísticas

### Population Stability Index

Se utiliza para comparar:

- Márgenes de decisión.
- Cantidad de términos activos.
- Longitud de los textos.

Interpretación provisional:

- PSI menor de `0.10`: cambio pequeño.
- PSI entre `0.10` y `0.25`: cambio relevante.
- PSI mayor o igual a `0.25`: cambio importante.

### Jensen-Shannon

Se utiliza para comparar:

- Distribución de categorías.
- Distribución de estados operativos.

## Archivos

```text
monitoring/
├── config/
│   ├── monitoring_config.json
│   ├── reference_profile.json
│   └── reference_predictions.csv
├── logs/
│   └── monitoring_events.jsonl
└── batches/
    └── archivos CSV por lote
```

## Consideraciones

Las señales de cambio estadístico no sustituyen la evaluación con etiquetas
reales.

Cuando se obtengan etiquetas posteriores deben calcularse también:

- Accuracy.
- Precision.
- Recall.
- F1 Macro.
- Matriz de confusión.
- Rendimiento por categoría.
- Diferencia entre predicciones automáticas y revisiones humanas.

Los textos de producción pueden contener información sensible. Antes de
registrar contenido completo deben definirse políticas de privacidad,
retención y anonimización.
