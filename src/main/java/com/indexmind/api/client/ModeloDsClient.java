package com.indexmind.api.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.indexmind.api.dto.CodigoError;
import com.indexmind.api.dto.ModeloHealthResponse;
import com.indexmind.api.dto.PredictRequest;
import com.indexmind.api.dto.PredictResponse;
import com.indexmind.api.dto.Resumen;
import com.indexmind.api.exception.ContenidoException;
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
public class ModeloDsClient {

    private final RestClient restClient;

    public ModeloDsClient(@Value("${ds.modelo.base-url}") String baseUrl,
                          @Value("${ds.modelo.timeout-ms}") long timeoutMs,
                          ObjectMapper objectMapper) {

        ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.DEFAULTS
                .withConnectTimeout(Duration.ofMillis(timeoutMs))
                .withReadTimeout(Duration.ofMillis(timeoutMs));

        ClientHttpRequestFactory factory = ClientHttpRequestFactories.get(settings);

        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .messageConverters(converters -> {
                    converters.removeIf(c -> c instanceof MappingJackson2HttpMessageConverter);
                    converters.add(new MappingJackson2HttpMessageConverter(objectMapper));
                })
                .build();
    }

    public ModeloHealthResponse consultarHealth() {
        try {
            return restClient.get()
                    .uri("/health")
                    .retrieve()
                    .body(ModeloHealthResponse.class);
        } catch (RestClientException ex) {
            return null; // si el servidor en python está caido o da timeout
        }
    }

    public PredictResponse consultarPrediccion(PredictRequest request) {
        try {
            return restClient.post()
                    .uri("/predict")
                    .body(request)
                    .retrieve()
                    .body(PredictResponse.class);
        } catch (RestClientException ex) {
            throw new ContenidoException("No hay respuesta del modelo", CodigoError.ERROR_MODELO, null);
        }
    }
}