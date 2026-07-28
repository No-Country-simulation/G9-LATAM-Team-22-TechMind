package com.indexmind.api.controller;

import com.indexmind.api.dto.HealthResponse;
import com.indexmind.api.service.ContenidoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class HealthController {
    @Autowired
    private ContenidoService service;
    @GetMapping("/health")
    public ResponseEntity<HealthResponse> disnibilidad () {
        boolean cargado = service.modeloDisponible();
        var status = cargado ? HealthResponse.Status.OK : HealthResponse.Status.ERROR;
        var response = new HealthResponse(status, cargado, "1.0");

        return cargado
                ? ResponseEntity.ok(response)
                : ResponseEntity.status(503).body(response);
    }
}
