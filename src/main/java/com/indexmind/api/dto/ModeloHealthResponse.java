package com.indexmind.api.dto;

public record ModeloHealthResponse(
        String status,
        boolean ready,
        String apiVersion,
        Integer wordFeatures,
        Integer charFeatures,
        Integer totalFeatures
) {
}
