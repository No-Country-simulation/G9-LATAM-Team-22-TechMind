package com.indexmind.api.controller;

import com.indexmind.api.service.ContenidoService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(HealthController.class)
class HealthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ContenidoService service;

    @Test
    @DisplayName("Debe devolver 200 OK cuando el modelo está disponible")
    void health_ModeloDisponible_Devuelve200() throws Exception {
        // dado que el servicio responde que el modelo está disponible
        when(service.modeloDisponible()).thenReturn(true);

        // cuando se consulta /api/v1/health
        mockMvc.perform(get("/api/v1/health"))
                // entoncese responde 200 OK y status ok
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"))
                .andExpect(jsonPath("$.modelo_cargado").value(true));
    }


    @Test
    @DisplayName("Debe devolver 503 Service Unavailable cuando el modelo no está disponible")
    void health_ModeloNoDisponible_Devuelve503() throws Exception {
        // dado que el servicio responde que el modelo no está disponible
        when(service.modeloDisponible()).thenReturn(false);

        // cuando se consulta /api/v1/health
        mockMvc.perform(get("/api/v1/health"))
                // entonces responde 503 Service Inavailable y status error
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value("error"))
                .andExpect(jsonPath("$.modelo_cargado").value(false));
    }
}