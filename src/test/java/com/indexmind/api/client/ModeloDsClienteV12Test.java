package com.indexmind.api.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.indexmind.api.dto.CodigoError;
import com.indexmind.api.dto.PredictRequestV12;
import com.indexmind.api.dto.PredictResponseV12;
import com.indexmind.api.exception.ContenidoException;
import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ModeloDsClientV12Test {

    @Test
    @DisplayName("Debe lanzar ERROR_MODELO en consultarPrediccion cuando el servidor v1.2 está caído")
    void consultarPrediccionV12_ServidorCaido_LanzaErrorModelo() {

        ModeloDsClientV12 client =
                new ModeloDsClientV12("http://localhost:9", 500, new ObjectMapper());

        ContenidoException ex = assertThrows(
                ContenidoException.class,
                () -> client.consultarPrediccion(
                        new PredictRequestV12(
                                List.of("texto"),
                                true,
                                8,
                                1
                        )
                )
        );

        assertThat(ex.getCodigo()).isEqualTo(CodigoError.ERROR_MODELO);
    }

    @Test
    @DisplayName("Debe deserializar correctamente una respuesta exitosa del modelo v1.2")
    void consultarPrediccionV12_RespuestaExitosa_DeserializaCorrectamente() throws IOException {

        HttpServer server = HttpServer.create(
                new InetSocketAddress(0),
                0
        );

        server.createContext("/predict", exchange -> {

            String json = """
                {
                  "model_version": "1.2.0-multilingual",
                  "model_status": "validated_experimental_candidate",
                  "n_inputs": 1,
                  "summary": {
                    "accepted": 1,
                    "review": 0,
                    "rejected_ood": 0,
                    "rejected_invalid": 0
                  },
                  "predictions": [
                    {
                      "index": 0,
                      "text": "Spring Boot es un framework para desarrollar aplicaciones backend con Java",
                      "valid_input": true,
                      "decision": "accepted",
                      "prediction": "backend",
                      "second_category": "frontend",
                      "decision_margin": 2.3803858648631717,
                      "domain_similarity_5nn": 0.605273962020874,
                      "tfidf_active_features": 170,
                      "reason": null,
                      "score_top1": 1.4541575075928974,
                      "score_top2": -0.9262283572702745,
                      "top_k": [
                        {
                          "category": "backend",
                          "score": 1.4541575075928974
                        },
                        {
                          "category": "frontend",
                          "score": -0.9262283572702745
                        }
                      ],
                      "explanation": null
                    }
                  ]
                }
                """;

            exchange.getResponseHeaders()
                    .set("Content-Type", "application/json; charset=UTF-8");

            byte[] bytes = json.getBytes(java.nio.charset.StandardCharsets.UTF_8);

            exchange.sendResponseHeaders(200, bytes.length);

            try (var outputStream = exchange.getResponseBody()) {
                outputStream.write(bytes);
            }
        });

        server.start();

        ModeloDsClientV12 client = new ModeloDsClientV12(
                "http://localhost:" + server.getAddress().getPort(),
                2000,
                new ObjectMapper()
        );

        PredictResponseV12 resultado;

        try {
            resultado = client.consultarPrediccion(
                    new PredictRequestV12(
                            List.of("Spring Boot es un framework para desarrollar aplicaciones backend con Java"),
                            true,
                            8,
                            4
                    )
            );
        } catch (ContenidoException ex) {
            throw ex;
        }

        assertThat(resultado).isNotNull();

        assertThat(resultado.predictions()).hasSize(1);

        assertThat(resultado.predictions().get(0).prediction())
                .isEqualTo("backend");

        assertThat(resultado.predictions().get(0).decision())
                .isEqualTo("accepted");

        assertThat(resultado.predictions().get(0).secondCategory())
                .isEqualTo("frontend");

        assertThat(resultado.predictions().get(0).decisionMargin())
                .isEqualTo(2.3803858648631717);

        server.stop(0);
    }
}
