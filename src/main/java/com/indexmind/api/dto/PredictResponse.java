package com.indexmind.api.dto;

import java.util.List;

public record PredictResponse(
        Resumen resumen,
        List<Resultado> resultados
) {
}
