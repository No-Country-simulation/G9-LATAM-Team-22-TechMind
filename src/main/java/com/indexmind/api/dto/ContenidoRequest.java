package com.indexmind.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record ContenidoRequest(
        @Size(max = 200)
        String titulo,
        @NotBlank @Size(min = 10, max = 5000)
        String texto
) {
}
