package com.indexmind.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

@Schema(description = "Objeto de entrdada con el contenido técnico a clasificar")
public record ContenidoRequest(
        @Schema(description = "Titulo del recurso tecnico")
        @Size(max = 200, message = "El titulo no debe exceder de los 200 caracteres")
        String titulo,

        @Schema(description = "Texto completo del contenido a analizar")
        @NotBlank(message = "El texto no puede estar vacio")
        @Size(min = 10, max = 5000, message = "El texto debe tener entre 10 y 5000 caracteres")
        String texto
) {
}
