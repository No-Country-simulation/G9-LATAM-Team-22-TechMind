package com.indexmind.api.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.Collections;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ModeloDsClientTest {

    @Test
    @DisplayName("Debe devolver null en consultarHealth cuando el servidor del modelo está caído")
    void consultarHealth_ServidorCaido_DevuelveNull() {
        // baseUrl apunta a un puerto sin nada escuchando -> RestClientException real
        ModeloDsClient client = new ModeloDsClient("http://localhost:9", 500, new ObjectMapper());
        ModeloHealthResponse resultado = client.consultarHealth();
        assertThat(resultado).isNull();
    }

    @Test
    @DisplayName("Debe lanzar ERROR_MODELO en consultarPrediccion cuando el servidor del modelo está caído")
    void consultarPrediccion_ServidorCaido_LanzaErrorModelo(){
        ModeloDsClient client = new ModeloDsClient("http://localhost:9", 500, new ObjectMapper());
        ContenidoException ex = assertThrows(ContenidoException.class,
                () -> client.consultarPrediccion(new PredictRequest(List.of("texto"), true, 15, 4)));
        assertThat(ex.getCodigo()).isEqualTo(CodigoError.ERROR_MODELO);
    }

    @Test
    @DisplayName("Debe devolver la respuesta clasificada cuando el modelo responde correctamente")
    void clasificar_RespuestaExitosa_DevuelveContenidoResponse()throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(0), 0); // puerto 0 = automático
        server.createContext("/predict", exchange -> {
            String json = """
                    {
                      "resumen": { "request_id": "test-id" },
                      "resultados": [
                        {
                          "categoria_predicha": "backend",
                          "segunda_categoria": "cloud",
                          "estado": "aceptada",
                          "requiere_revision": false,
                          "prediccion_utilizable": true,
                          "puntuacion_ganadora": 0.35,
                          "puntuacion_segunda": 0.0,
                          "margen_decision": 0.0,
                          "nivel_margen": "Bajo",
                          "characters": 12,
                          "words": 2,
                          "valid_input": true,
                          "validation_message": "Inferencia completada.",
                          "terminos_activos": 0, 
                          "word_features_activas": 0, 
                          "char_features_activas": 0, 
                          "features_activas_total": 0,
                          "advertencias": ["La cobertura depende únicamente de n-gramas de caracteres."], 
                          "accion_recomendada": "Predicción utilizable automáticamente", 
                          "explicacion": null 
                        }
                      ]
                    }
                    """;
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            byte[] bytes = json.getBytes();
            exchange.sendResponseHeaders(200, bytes.length);
            exchange.getResponseBody().write(bytes);
            exchange.getResponseBody().close();
        });
        server.start();
        ModeloDsClient client = new ModeloDsClient("http://localhost:" + server.getAddress().getPort(), 2000, new ObjectMapper());

        PredictResponse resultado = client.consultarPrediccion(new PredictRequest(List.of("texto"), true, 15, 4));

        assertThat(resultado.resultados()).hasSize(1);
        assertThat(resultado.resultados().get(0).categoriaPredicha()).isEqualTo("backend");

        server.stop(0);
    }
}