package com.indexmind.api.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record ModelInfoResponse(
        String apiVersion,
        String version,
        String status,
        String architecture,
        String classifier,
        double classifierC,
        String embeddingModel,
        int embeddingDimension,
        List<String> classes,
        DomainControl domainControl,
        ConfidenceControl confidenceControl,
        String artifactSha256,
        boolean scoresAreProbabilities
) {
}
