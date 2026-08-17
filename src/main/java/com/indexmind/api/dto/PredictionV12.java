package com.indexmind.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record PredictionV12(
        int index,
        String text,
        boolean validInput,
        String decision,
        String prediction,
        String secondCategory,
        Double decisionMargin,

        @JsonProperty("domain_similarity_5nn")
        Double domainSimilarity5nn,
        int tfidfActiveFeatures,
        String reason,
        Double scoreTop1,
        Double scoreTop2,
        List<TopKPredictionV12> topK,
        ExplanationV12 explanation
) {
}
