package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record PredictRequestV12(
        List<String> texts,
        boolean includeExplanation,
        int explanationTopN,
        Integer topK
) {
}
