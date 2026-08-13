package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record Resultado(
        // Bloque 1: identificación y estado
        String categoriaPredicha,
        String segundaCategoria,
        String estado,
        boolean requiereRevision,
        boolean prediccionUtilizable,

        // Bloque 2: scores
        Double puntuacionGanadora,
        Double puntuacionSegunda,
        Double margenDecision,
        String nivelMargen,

        // Bloque 3: metadatos del texto
        Integer characters,
        Integer words,
        Boolean validInput,
        String validationMessage,

        // Bloque 4: cobertura de features
        Integer terminosActivos,
        Integer wordFeaturesActivas,
        Integer charFeaturesActivas,
        /**
         * Cobertura total de features activas (word + char).
         * ⚠️ Usar este campo para decidir cobertura, NO wordFeaturesActivas de forma aislada.
         * Ver guía backend v1.1.0, sección 7.
         */
        Integer featuresActivasTotal,

        List<String>advertencias,
        String accionRecomendada,
        Explicacion explicacion
) {
}
