package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record ModeloHealthResponse(
        String status,
        boolean ready,
        String apiVersion,
        Integer wordFeatures,
        Integer charFeatures,
        Integer totalFeatures
) {
}
