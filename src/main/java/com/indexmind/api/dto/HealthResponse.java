package com.indexmind.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record HealthResponse(
        Status status,
        boolean modeloCargado,
        String version
) {
    public enum Status{
        @JsonProperty("ok")
        OK,
        @JsonProperty("error")
        ERROR
    }
}
