package com.indexmind.api.service;

import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import com.indexmind.api.dto.HealthResponse;

public interface ContenidoService {
    ContenidoResponse clasificar (ContenidoRequest request);
    boolean modeloDisponible();
}
