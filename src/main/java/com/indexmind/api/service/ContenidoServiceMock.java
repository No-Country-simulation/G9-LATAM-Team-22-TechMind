package com.indexmind.api.service;

import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ContenidoServiceMock implements ContenidoService {
    @Override
    public ContenidoResponse clasificar(ContenidoRequest request) {
        return new ContenidoResponse("Backend", 0.89F, List.of("Java", "Spring Boot", "API REST"));
    }

    @Override
    public Boolean modeloDisponible() {
        return true;
    }
}
