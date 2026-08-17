package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClientV12;
import com.indexmind.api.dto.CodigoError;
import com.indexmind.api.dto.ContenidoRequest;
import com.indexmind.api.dto.PredictResponseV12;
import com.indexmind.api.dto.PredictionV12;
import com.indexmind.api.exception.ContenidoException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContenidoServiceImplV12Test {

    @Mock
    private ModeloDsClientV12 modeloDsClientV12;

    private ContenidoServiceImplV12 service;

    @BeforeEach
    void setUp() {
        service = new ContenidoServiceImplV12(modeloDsClientV12);
    }

    @Test
    void clasificar_DecisionAccepted_DevuelveContenidoResponseSinRevision() {
        var prediction = crearPrediction("accepted", "backend", 1.84, null);
        var response = crearPredictResponse(prediction);
        when(modeloDsClientV12.consultarPrediccion(any())).thenReturn(response);

        var resultado = service.clasificar(new ContenidoRequest("Titulo", "Un texto de prueba con más de diez caracteres."));

        assertThat(resultado.categoria()).isEqualTo("backend");
        assertThat(resultado.requiereRevision()).isFalse();
    }

    @Test
    void clasificar_DecisionReview_DevuelveContenidoResponseConRevision() {
        var prediction = crearPrediction("review", "cloud", 0.75, null);
        var response = crearPredictResponse(prediction);
        when(modeloDsClientV12.consultarPrediccion(any())).thenReturn(response);

        var resultado = service.clasificar(new ContenidoRequest("Titulo", "Un texto de prueba con más de diez caracteres."));

        assertThat(resultado.categoria()).isEqualTo("cloud");
        assertThat(resultado.requiereRevision()).isTrue();
    }

    @Test
    void clasificar_DecisionRejectedOod_LanzaContenidoException() {
        var prediction = crearPrediction("rejected_ood", "datascience", -0.5, "Soporte semántico insuficiente");
        var response = crearPredictResponse(prediction);
        when(modeloDsClientV12.consultarPrediccion(any())).thenReturn(response);

        var request = new ContenidoRequest("Titulo", "Un texto fuera de dominio para probar rechazo.");

        assertThatThrownBy(() -> service.clasificar(request))
                .isInstanceOf(ContenidoException.class)
                .extracting(ex -> ((ContenidoException) ex).getCodigo())
                .isEqualTo(CodigoError.PREDICCION_RECHAZADA_OOD);
    }

    @Test
    void clasificar_DecisionRejectedInvalid_LanzaContenidoException() {
        var prediction = crearPrediction("rejected_invalid", null, 0.0, "Entrada inválida");
        var response = crearPredictResponse(prediction);
        when(modeloDsClientV12.consultarPrediccion(any())).thenReturn(response);

        var request = new ContenidoRequest("Titulo", "Un texto de prueba con más de diez caracteres.");

        assertThatThrownBy(() -> service.clasificar(request))
                .isInstanceOf(ContenidoException.class)
                .extracting(ex -> ((ContenidoException) ex).getCodigo())
                .isEqualTo(CodigoError.PREDICCION_RECHAZADA_OOD);
    }

    @Test
    void clasificar_PrediccionesVacias_LanzaContenidoExceptionConRespuestaModeloInvalida() {
        var response = new PredictResponseV12(
                "1.2.0-multilingual", "validated_experimental_candidate", 0,
                Map.of(),
                List.of() // predictions vacío -> caso que estamos probando
        );
        when(modeloDsClientV12.consultarPrediccion(any())).thenReturn(response);

        var request = new ContenidoRequest("Titulo", "Un texto de prueba con más de diez caracteres.");

        assertThatThrownBy(() -> service.clasificar(request))
                .isInstanceOf(ContenidoException.class)
                .extracting(ex -> ((ContenidoException) ex).getCodigo())
                .isEqualTo(CodigoError.RESPUESTA_MODELO_INVALIDA);
    }

    // --- Helpers ---

    private PredictionV12 crearPrediction(String decision, String prediction, double scoreTop1, String reason) {
        return new PredictionV12(
                0, "texto de prueba", true,
                decision, prediction, "cloud",
                0.9, 0.5, 100,
                reason,
                scoreTop1, 0.3,
                List.of(),
                null // explanation
        );
    }

    private PredictResponseV12 crearPredictResponse(PredictionV12 prediction) {
        return new PredictResponseV12(
                "1.2.0-multilingual", "validated_experimental_candidate", 1,
                Map.of(),
                List.of(prediction)
        );
    }
}
