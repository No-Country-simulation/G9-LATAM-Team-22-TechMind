package com.indexmind.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.ContenidoResponse;
import com.indexmind.api.service.ContenidoService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;


@WebMvcTest(ContenidoController.class)
class ContenidoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ContenidoService service;

    @Test
    @DisplayName("Debe clasificar contenido correctamente y devolver 200 OK")
    void clasificar_DatosValidos_Devuelve200() throws Exception {
        // datos de entrada válidos
        ContenidoRequest request = new ContenidoRequest("Prueba de API", "Este es un texto válido para clasificar contenido en el backend.");

        // mock de la respuesta esperada del servicio
        ContenidoResponse responseMock = new ContenidoResponse("Backend", 0.89F, List.of("Java", "Spring Boot"));
        when(service.clasificar(any(ContenidoRequest.class))).thenReturn(responseMock);

        // petición POST a /api/v1/contenido
        mockMvc.perform(post("/api/v1/contenido")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.categoria").value("Backend"))
                .andExpect(jsonPath("$.probabilidad").value(0.89))
                .andExpect(jsonPath("$.informacion_adicional[0]").value("Java"));
    }
}