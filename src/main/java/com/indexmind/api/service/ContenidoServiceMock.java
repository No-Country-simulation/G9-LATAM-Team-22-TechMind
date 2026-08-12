package com.indexmind.api.service;

import com.indexmind.api.dto.CodigoError;
import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.stereotype.Service;

import java.util.List;

//@Service
public class ContenidoServiceMock implements ContenidoService {
    @Override
    public ContenidoResponse clasificar(ContenidoRequest request) {
        if (!modeloDisponible()) {
            throw new ContenidoException(
                    "No fue posible obtener una respuesta del modelo de clasificación.",
                    CodigoError.ERROR_MODELO,
                    null
            );
        }
        return new ContenidoResponse("Backend", 0.89F, List.of("Java", "Spring Boot", "API REST"));
    }

    @Override
    public boolean modeloDisponible() {
        return true;
    }
}
