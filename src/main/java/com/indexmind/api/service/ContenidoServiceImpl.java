package com.indexmind.api.service;

import com.indexmind.api.client.ModeloDsClient;
import com.indexmind.api.dto.*;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

import java.text.Normalizer;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
@Profile("v11")
public class ContenidoServiceImpl implements ContenidoService {

    private static final Set<String> stopWords = Set.of(
            "el", "la", "los", "las", "un", "una", "unos", "unas", "del", "al",
            "de", "en", "con", "por", "para", "sin", "sobre", "entre", "desde", "hasta",
            "y", "o", "pero", "si", "que", "como", "cuando", "donde",
            "su", "sus", "esto", "esta", "este", "estos", "estas", "eso", "esa", "ese",
            "es", "son", "ser", "estar", "hay", "tiene", "puede", "permite",
            "utilizando", "utiliza", "usando", "usa", "creacion", "crear",
            "contenido", "texto", "material", "explica", "presenta", "muestra"
    );

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
        var score = (float) Math.max(0.0, Math.min(1.0, resultado.puntuacionGanadora()));
        var informacionAdicional = extraerInformacionAdicional(resultado, request.texto());
        var response = new ContenidoResponse(categoria, score, informacionAdicional, false);
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
                .map(t -> extraerPalabraCompleta(t.term(), textoOriginal))
                .filter(t -> Objects.nonNull(t))
                .toList();

        return Stream.concat(palabrasWord.stream(), palabrasChar.stream())
                .filter(t -> !stopWords.contains(eliminarAcentos(t.toLowerCase())))
                .collect(Collectors.toMap(t -> t.toLowerCase().trim(), t -> t.trim(), (existente, nuevo) -> existente))
                .values()
                .stream()
                .toList();
    }

    private String extraerPalabraCompleta(String fragmentoChar, String textoOriginal) {
        Pattern pattern = Pattern.compile(
                "\\b\\w*" + Pattern.quote(fragmentoChar.trim()) + "\\w*\\b",
                Pattern.CASE_INSENSITIVE
        );
        Matcher matcher = pattern.matcher(textoOriginal);
        if (matcher.find()) {
            return matcher.group(); // devuelve la palabra tal cual está escrita en el texto original
        }
        return null; // si no se encuentra, lo descartamos
    }

    private String eliminarAcentos(String textoOriginal){
        String textoDescompuesto = Normalizer.normalize(textoOriginal, Normalizer.Form.NFD);
        Pattern patronAcentos = Pattern.compile("\\p{M}");
        String textoLimpio = patronAcentos.matcher(textoDescompuesto).replaceAll("");
        return textoLimpio;
    }
}
