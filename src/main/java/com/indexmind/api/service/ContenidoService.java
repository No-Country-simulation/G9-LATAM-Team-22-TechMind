package com.indexmind.api.service;

import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;

public interface ContenidoService {
    ContenidoResponse clasificar (ContenidoRequest request);
    Boolean modeloDisponible();
}
