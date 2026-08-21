package com.indexmind.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;

public record ErrorDetail(
        CodigoError codigo,
        String mensaje,
        @JsonInclude(JsonInclude.Include.ALWAYS) // Indica null sin omitir el campo
        String campo,
        Instant timestamp
) {
}
