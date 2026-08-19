package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClientV12;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
@Profile("v12")
public class ContenidoServiceImplV12 implements ContenidoService {

    private final ModeloDsClientV12 modeloDsClientV12;

    public ContenidoServiceImplV12(ModeloDsClientV12 modeloDsClientV12) {
        this.modeloDsClientV12 = modeloDsClientV12;
    }

    @Override
    public boolean modeloDisponible() {
        ModeloHealthResponseV12 health = modeloDsClientV12.consultarHealth();
        return health != null && health.modelLoaded();
    }

    @Override
    public ContenidoResponse clasificar(ContenidoRequest request) {
        PredictRequestV12 predictRequest = new PredictRequestV12(
                Collections.singletonList(request.texto()),
                true, // includeExplanation -> true para poder llenar informacionAdicional
                8,    // explanationTopN
                4     // topK
        );

        PredictResponseV12 predictResponse = modeloDsClientV12.consultarPrediccion(predictRequest);

        if (predictResponse == null || predictResponse.predictions().isEmpty()) {
            throw new ContenidoException("El modelo no devolvió resultados", CodigoError.RESPUESTA_MODELO_INVALIDA, null);
        }

        var resultado = predictResponse.predictions().get(0);

        return switch (resultado.decision()) {
            case "accepted" -> construirRespuesta(resultado, request.texto(), false);
            case "review" -> construirRespuesta(resultado, request.texto() ,true);
            case "rejected_ood", "rejected_invalid" -> throw new ContenidoException(
                    "El modelo rechazó la clasificación: " + resultado.reason(),
                    CodigoError.PREDICCION_RECHAZADA_OOD,
                    "texto"
            );
            default -> throw new ContenidoException(
                    "Decision desconocida: " + resultado.decision(),
                    CodigoError.RESPUESTA_MODELO_INVALIDA,
                    null
            );
        };
    }

    private ContenidoResponse construirRespuesta(PredictionV12 resultado, String texto, boolean requiereRevision) {
        var categoria = resultado.prediction();
        var score = resultado.scoreTop1() != null ? resultado.scoreTop1().floatValue() : 0f; // TODO: sigue sin ser una score real, ver sección 5.3 de la guía
        var informacionAdicional = extraerInformacionAdicional(resultado, texto);
        return new ContenidoResponse(categoria, score, informacionAdicional, requiereRevision);
    }

    private List<String> extraerInformacionAdicional(PredictionV12 resultado, String textoOriginal) {
        if (resultado.explanation() == null || !resultado.explanation().available()) {
            return List.of();
        }

        List<String> palabrasWord = resultado.explanation().terms().stream()
                .filter(t -> t.feature().startsWith("word__"))
                .map(t -> t.feature().substring("word__".length()))
                .toList();

        List<String> palabrasChar = resultado.explanation().terms().stream()
                .filter(t -> t.feature().startsWith("char__"))
                .map(t -> t.feature().substring("char__".length()).trim())
                .filter(t -> t.length() >= 5)
                .filter(textoOriginal.toLowerCase()::contains)
                .toList();

        return Stream.concat(palabrasWord.stream(), palabrasChar.stream())
                .collect(Collectors.toMap(String::toLowerCase, t -> t, (existente, nuevo) -> existente))
                .values()
                .stream()
                .toList();
    }


}