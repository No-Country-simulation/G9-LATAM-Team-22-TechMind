package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClientV12;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

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
            case "accepted" -> construirRespuesta(resultado, false);
            case "review" -> construirRespuesta(resultado, true);
            case "rejected_ood", "rejected_invalid" -> throw new ContenidoException(
                    "El modelo rechazó la clasificación: " + resultado.reason(),
                    CodigoError.PREDICCION_RECHAZADA_OOD, // ⚠️ confirmar nombre exacto (OOD vs ODD) con tu compañero
                    "texto"
            );
            default -> throw new ContenidoException(
                    "Decision desconocida: " + resultado.decision(),
                    CodigoError.RESPUESTA_MODELO_INVALIDA,
                    null
            );
        };
    }

    private ContenidoResponse construirRespuesta(PredictionV12 resultado, boolean requiereRevision) {
        var categoria = resultado.prediction();
        var probabilidad = resultado.scoreTop1() != null ? resultado.scoreTop1().floatValue() : 0f; // TODO: sigue sin ser una probabilidad real, ver sección 5.3 de la guía
        var informacionAdicional = extraerInformacionAdicional(resultado);
        return new ContenidoResponse(categoria, probabilidad, informacionAdicional, requiereRevision);
    }

    private List<String> extraerInformacionAdicional(PredictionV12 resultado) {
        if (resultado.explanation() == null || !resultado.explanation().available()) {
            return List.of();
        }
        return resultado.explanation().terms().stream()
                .map(ExplanationTermV12::feature)
                .toList();
    }
}