package com.indexmind.api.dto;

import java.util.List;

public record PredictRequest(
        List<String> textos,
        boolean incluirExplicacion,
        int topNExplicacion,
        int topK
) {
}
