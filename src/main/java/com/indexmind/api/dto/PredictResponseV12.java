package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;
import java.util.Map;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record PredictResponseV12(
        String modelVersion,
        String modelStatus,
        int nInputs,
        Map<String, Integer> summary,
        List<PredictionV12> predictions
) {
}
