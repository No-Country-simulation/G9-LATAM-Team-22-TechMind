package com.indexmind.api.dto;

public record Termino(
        String term,
        String featureType,
        Double tfidf,
        Double coefficient,
        Double contribution
) {
}
