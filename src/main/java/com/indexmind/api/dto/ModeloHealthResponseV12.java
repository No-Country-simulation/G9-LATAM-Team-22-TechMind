package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record ModeloHealthResponseV12(
        String status,
        boolean modelLoaded,
        String apiVersion,
        String modelVersion
) {
}