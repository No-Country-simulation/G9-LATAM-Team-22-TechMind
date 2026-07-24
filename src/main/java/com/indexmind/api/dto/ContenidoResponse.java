package com.indexmind.api.dto;

import jakarta.validation.constraints.Size;

import java.util.List;

public record ContenidoResponse(
        String categoria,
        float probabilidad,
        List<String> informacionAdicional
) {
}
