package com.indexmind.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;

import java.util.List;

@Schema(description = "Resultado del análisis y clasificación del contenido técnico")
public record ContenidoResponse(
        @Schema(description = "Categoría predicha para el contenido")
        String categoria,

        @Schema(description = "Nivel de confianza o probabilidad calculada por el modelo (0.0 a 1.0)")
        float probabilidad,

        @Schema(description = "Información adicional o palabras clave identificadas")
        List<String> informacionAdicional,

        boolean requiereRevision // NUEVO
) {
}
