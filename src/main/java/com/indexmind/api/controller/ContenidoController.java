package com.indexmind.api.controller;

import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import com.indexmind.api.service.ContenidoService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ContenidoController {
    @Autowired
    private ContenidoService service;

    @PostMapping("/contenido")
    public ResponseEntity<ContenidoResponse> analizar (@Valid @RequestBody ContenidoRequest request){
        return ResponseEntity.ok(service.clasificar(request));
    }
}
