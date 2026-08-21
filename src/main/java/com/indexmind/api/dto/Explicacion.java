package com.indexmind.api.dto;

import java.util.List;

public record Explicacion(
        List<Termino> positiveTerms,
        List<Termino> negativeTerms,
        List<Termino> differentialTerms,
        String warning
) {
}
