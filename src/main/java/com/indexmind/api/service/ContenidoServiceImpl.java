package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClient;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ContenidoServiceImpl implements ContenidoService{

    private final ModeloDsClient modeloDsClient;

    public ContenidoServiceImpl(ModeloDsClient modeloDsClient) {
        this.modeloDsClient = modeloDsClient;
    }

    @Override
    public boolean modeloDisponible() {
        ModeloHealthResponse health = modeloDsClient.consultarHealth();
        // el modelo se considera disponible solo si responde y su campo 'ready' es verdadero
        return health != null && health.ready();
    }

    @Override
    public ContenidoResponse clasificar(ContenidoRequest request) {
        // si el modelo no está listo/disponible, lanzar error 503/500
        if(!modeloDisponible()) {
            throw new ContenidoException("El modelo no está disponible", CodigoError.ERROR_MODELO, null);
        }

        // construir la petición hacia Python (PredictRequest)
        PredictRequest predictRequest = new PredictRequest(
                List.of(request.texto()),
                true, // incluirExplicación
                5, // topNExplicacion
                1 // topK
        );

        // consultar el modelo (ModeloDsClient ya captura timeouts/fallos de conexión y lanza ERROR_MODELO)
        PredictResponse response = modeloDsClient.consultarPrediccion(predictRequest);

        // validar que la respuesta contenga datos validos
        validarRespuestaModelo(response);

        Resultado resultado = response.resultados().get(0);

        // validar si la predicción fue rechazada por el modelo
        if(!resultado.prediccionUtilizable() || "rechazada".equalsIgnoreCase(resultado.estado())) {
            throw new ContenidoException(
                    "El modelo rechazó el procesamiento del texto: " + resultado.validationMessage(),
                    CodigoError.PREDICCION_RECHAZADA,
                    "texto"
            );
        }

        // mapeo temporal
        float probabilidad = resultado.puntuacionGanadora() != null ? resultado.puntuacionGanadora().floatValue() : 0.0f;
        return new ContenidoResponse(resultado.categoriaPredicha(), probabilidad, List.of());
    }

    private void validarRespuestaModelo(PredictResponse response) {
        if (response == null || response.resultados() == null || response.resultados().isEmpty()) {
            throw new ContenidoException("La respuesta del modelo fue nula o malformada", CodigoError.RESPUESTA_MODELO_INVALIDA, null);
        }
    }
}
