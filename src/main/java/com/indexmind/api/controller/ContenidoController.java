package com.indexmind.api.controller;

import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import com.indexmind.api.service.ContenidoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
@Tag(name = "Contenido", description = "Endpoints para la gestión y clasificación del contenido técnico")
public class ContenidoController {
    @Autowired
    private ContenidoService service;

    @PostMapping("/contenido")
    @Operation(
            summary = "Clasificar contenido técnico",
            description = "Recibe un texto técnico en formato JSON, ejecuta las validaciones y devuelve la categoría procesada"
    )
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Procesamiento exitoso"),
            @ApiResponse(responseCode = "400", description = "Petición inválida: los datos de entrada no cumplen con las reglas de validación")
    })
    public ResponseEntity<ContenidoResponse> analizar (@Valid @RequestBody ContenidoRequest request){
        return ResponseEntity.ok(service.clasificar(request));
    }
}
