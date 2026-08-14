package com.indexmind.api.service;

import com.indexmind.api.client.*;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContenidoServiceImplTest {

    @Mock
    private ModeloDsClient modeloDsClient;

    @Test
    @DisplayName("Debe devolver un ContenidoResponse cuando el modelo clasifica correctamente")
    void clasificar_RespuestaExitosa_DevuelveContenidoResponse() {
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);
        var resultadoAceptadoMock = crearResultadoBase(true);
        PredictResponse response = new PredictResponse(new Resumen("test-request-id"), Collections.singletonList(resultadoAceptadoMock));
        when(modeloDsClient.consultarPrediccion(any())).thenReturn(response);
        ContenidoResponse resultado = service.clasificar(new ContenidoRequest("Titulo de prueba", "Un texto de prueba con más de diez caracteres."));
        assertThat(resultado.categoria()).isEqualTo("backend");
        assertThat(resultado.probabilidad()).isEqualTo(0.35f);
        assertThat(resultado.informacionAdicional()).isEmpty();
    }

    private Resultado crearResultadoBase(boolean prediccionUtilizable){
        return new Resultado(
                "backend",          // categoriaPredicha
                "cloud",                  // segundaCategoria
                "aceptada",     // estado
                false,                   // requiereRevision
                prediccionUtilizable,                  // prediccionUtilizable

                0.35,                    // puntuacionGanadora
                0.0,                    // puntuacionSegunda
                0.0,                    // margenDecision
                "Bajo",                 // nivelMargen

                12,                     // characters (texto muy corto)
                2,                      // words
                true,                  // validInput
                "Inferencia completada.", // validationMessage

                0,                      // terminosActivos
                0,                      // wordFeaturesActivas
                0,                      // charFeaturesActivas
                0,                      // featuresActivasTotal

                List.of("La cobertura depende únicamente de n-gramas de caracteres."), // advertencias
                "Predicción utilizable automáticamente",             // accionRecomendada
                null                    // explicacion
        );
    }

    @Test
    @DisplayName("Debe lanzar RESPUESTA_MODELO_INVALIDA cuando el modelo no devuelve resultados")
    void clasificar_ResultadosVacio_LanzaRespuestaModeloInvalida(){
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);
        PredictResponse response = new PredictResponse(
                new Resumen("test-request-id"),
                Collections.emptyList() // <-- la clave del test
        );
        when(modeloDsClient.consultarPrediccion(any())).thenReturn(response);
        ContenidoException ex = assertThrows(ContenidoException.class, () -> service.clasificar(new ContenidoRequest("Titulo", "Un texto valido de prueba")));
        assertThat(ex.getCodigo()).isEqualTo(CodigoError.RESPUESTA_MODELO_INVALIDA);
    }

    @Test
    @DisplayName("Debe lanzar PREDICCION_RECHAZADA cuando el modelo marca la predicción como no utilizable")
    void clasificar_PrediccionNoUtilizable_LanzaPrediccionRechazada(){
        Resultado resultado = crearResultadoBase(false);
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);
        PredictResponse response = new PredictResponse(
                new Resumen("test-request-id"),
                Collections.singletonList(resultado)
        );
        when(modeloDsClient.consultarPrediccion(any())).thenReturn(response);
        ContenidoException ex = assertThrows(ContenidoException.class, () -> service.clasificar(new ContenidoRequest("Titulo", "Un texto valido de prueba")));
        assertThat(ex.getCampo()).isEqualTo("texto");
        assertThat(ex.getCodigo()).isEqualTo(CodigoError.PREDICCION_RECHAZADA);
    }

    @Test
    @DisplayName("Debe propagar ERROR_MODELO cuando el cliente del modelo falla")
    void clasificar_ClienteLanzaErrorModelo_PropagaExcepcion(){
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);
        when(modeloDsClient.consultarPrediccion(any())).thenThrow(new ContenidoException("No hay respuesta del modelo", CodigoError.ERROR_MODELO, null));
        ContenidoException ex = assertThrows(ContenidoException.class, () -> service.clasificar(new ContenidoRequest("Titulo", "Un texto valido de prueba")));
        assertThat(ex.getCodigo()).isEqualTo(CodigoError.ERROR_MODELO);
    }

    @Test
    @DisplayName("Debe devolver true cuando el modelo está disponible")
    void modeloDisponible_ModeloListo_DevuelveTrue() {
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);

        ModeloHealthResponse health = new ModeloHealthResponse(
                "ok",
                true,
                "1.0.0",
                30000,
                30000,
                60000
        );

        when(modeloDsClient.consultarHealth()).thenReturn(health);
        boolean disponible = service.modeloDisponible();
        assertThat(disponible).isTrue();
    }

    @Test
    @DisplayName("Debe devolver false cuando el modelo no está listo")
    void modeloDisponible_ModeloNoListo_DevuelveFalse() {
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);

        ModeloHealthResponse health = new ModeloHealthResponse(
                "ok",
                false,
                "1.0.0",
                30000,
                30000,
                6000
        );

        when(modeloDsClient.consultarHealth()).thenReturn(health);
        boolean disponible = service.modeloDisponible();
        assertThat(disponible).isFalse();
    }

    @Test
    @DisplayName("Debe devolver false cuando el modelo no responde")
    void modeloDisponible_ModeloNoResponde_DevuelveFalse() {
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);

        when(modeloDsClient.consultarHealth()).thenReturn(null);
        boolean disponible = service.modeloDisponible();
        assertThat(disponible).isFalse();
    }


    @Test
    @DisplayName("Debe deduplicar fragmentos con espacios y filtrar stopwords en información adicional")
    void clasificar_ConDuplicadosYStopwords_DevuelveInformacionLimpia() {
        ContenidoServiceImpl service = new ContenidoServiceImpl(modeloDsClient);

        List<Termino> positiveTerms = List.of(
                new Termino("pring ", "char", 0.0, 0.0, 0.0),
                new Termino("pring", "char", 0.0, 0.0, 0.0),
                new Termino("este", "word", 0.0, 0.0, 0.0)
        );

        Explicacion explicacion = new Explicacion(positiveTerms, List.of(), List.of(), "warning");

        Resultado resultadoMock = new Resultado(
                "backend", "cloud", "aceptada", false, true,
                0.45, 0.0, 0.0, "Media",
                132, 21, true, "Inferencia completada.",
                0, 0, 0, 0,
                List.of(), "Predicción utilizable automáticamente",
                explicacion
        );

        PredictResponse response = new PredictResponse(new Resumen("test-id"), List.of(resultadoMock));
        when(modeloDsClient.consultarPrediccion(any())).thenReturn(response);

        ContenidoRequest request = new ContenidoRequest(
                "titulo",
                "En este contenido se presentan los conceptos básicos para la creación de APIs REST utilizando Java y Spring Boot."
        );

        ContenidoResponse resultado = service.clasificar(request);

        assertThat(resultado.informacionAdicional()).containsExactly("Spring");
        assertThat(resultado.informacionAdicional()).doesNotContain("este", "Este");
    }
}