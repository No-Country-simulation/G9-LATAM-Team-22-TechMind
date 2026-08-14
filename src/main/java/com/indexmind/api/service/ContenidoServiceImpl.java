package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClient;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
public class ContenidoServiceImpl implements ContenidoService {

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
        PredictRequest predictRequest = new PredictRequest(Collections.singletonList(request.texto()), true, 15, 4);
        PredictResponse predictResponse = modeloDsClient.consultarPrediccion(predictRequest);

        if (predictResponse.resultados().isEmpty()) {
            throw new ContenidoException("El modelo invalido la respuesta", CodigoError.RESPUESTA_MODELO_INVALIDA, null);
        }

        var resultado = predictResponse.resultados().get(0);

        if (!resultado.prediccionUtilizable()) {
            throw new ContenidoException("El modelo rechazo el procesamiento del texto: " + resultado.validationMessage(), CodigoError.PREDICCION_RECHAZADA, "texto");
        }

        var categoria = resultado.categoriaPredicha();
        var probabilidad = (float) Math.max(0.0, Math.min(1.0, resultado.puntuacionGanadora()));
        var informacionAdicional = extraerInformacionAdicional(resultado, request.texto());
        var response = new ContenidoResponse(categoria, probabilidad, informacionAdicional);
        return response;
    }

    private List<String> extraerInformacionAdicional(Resultado resultado, String textoOriginal) {
        if (resultado.explicacion() == null) {
            return List.of();
        }

        List<Termino> terminos = resultado.explicacion().positiveTerms();

        List<String> palabrasWord = terminos.stream()
                .filter(t -> t.featureType().equals("word"))
                .map(t -> t.term())
                .toList();

        List<String> palabrasChar = terminos.stream()
                .filter(t -> t.featureType().equals("char"))
                .map(t -> t.term())
                .filter(t -> t.length() >= 5)
                .filter(t -> textoOriginal.contains(t))
                .toList();

        return Stream.concat(palabrasWord.stream(), palabrasChar.stream())
                .collect(Collectors.toMap(String::toLowerCase, t -> t, (existente, nuevo) -> existente))
                .values()
                .stream()
                .toList();
    }
}
