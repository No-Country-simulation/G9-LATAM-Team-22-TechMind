package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record ExplanationV12(
        boolean available,
        String scope,
        String note,
        List<ExplanationTermV12> terms
) {
}
