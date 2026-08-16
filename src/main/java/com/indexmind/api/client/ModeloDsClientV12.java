package com.indexmind.api.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.indexmind.api.dto.ModeloHealthResponseV12;
import com.indexmind.api.dto.ModelInfoResponse;
import com.indexmind.api.dto.PredictRequestV12;
import com.indexmind.api.dto.PredictResponseV12;
import com.indexmind.api.exception.ContenidoException;
import com.indexmind.api.dto.CodigoError;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.ClientHttpRequestFactories;
import org.springframework.boot.web.client.ClientHttpRequestFactorySettings;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.time.Duration;

@Component
public class ModeloDsClientV12 {

    private final RestClient restClient;

    public ModeloDsClientV12(
            @Value("${ds.modelo.base-url}") String baseUrl,
            @Value("${ds.modelo.timeout-ms}") long timeoutMs,
            ObjectMapper objectMapper) {

        ClientHttpRequestFactorySettings settings =
                ClientHttpRequestFactorySettings.DEFAULTS
                        .withConnectTimeout(Duration.ofMillis(timeoutMs))
                        .withReadTimeout(Duration.ofMillis(timeoutMs));

        ClientHttpRequestFactory factory =
                ClientHttpRequestFactories.get(settings);

        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .messageConverters(converters -> {
                    converters.removeIf(
                            c -> c instanceof MappingJackson2HttpMessageConverter
                    );
                    converters.add(
                            new MappingJackson2HttpMessageConverter(objectMapper)
                    );
                })
                .build();
    }

    public ModeloHealthResponseV12 consultarHealth() {
        try {
            return restClient.get()
                    .uri("/health")
                    .retrieve()
                    .body(ModeloHealthResponseV12.class);
        } catch (RestClientException ex) {
            return null;
        }
    }

    public ModelInfoResponse consultarModelInfo() {
        try {
            return restClient.get()
                    .uri("/model-info")
                    .retrieve()
                    .body(ModelInfoResponse.class);
        } catch (RestClientException ex) {
            return null;
        }
    }

    public PredictResponseV12 consultarPrediccion(
            PredictRequestV12 request) {

        try {
            return restClient.post()
                    .uri("/predict")
                    .body(request)
                    .retrieve()
                    .body(PredictResponseV12.class);

        } catch (RestClientException ex) {
            throw new ContenidoException(
                    "No hay respuesta del modelo",
                    CodigoError.ERROR_MODELO,
                    null
            );
        }
    }
}
