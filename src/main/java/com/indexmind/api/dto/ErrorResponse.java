package com.indexmind.api.dto;

import java.time.format.DateTimeFormatter;

public record ErrorResponse(
        ErrorDetail error
) {
}
