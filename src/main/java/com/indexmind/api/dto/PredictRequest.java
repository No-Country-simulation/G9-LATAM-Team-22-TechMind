package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record PredictRequest(
        List<String> textos,
        boolean incluirExplicacion,
        int topNExplicacion,
        int topK
) {
}
