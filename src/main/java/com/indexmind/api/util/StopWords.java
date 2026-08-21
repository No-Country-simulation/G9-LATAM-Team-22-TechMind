package com.indexmind.api.util;

import java.util.Set;

/**
 * Palabras vacías (stopwords) en español, usadas para filtrar
 * información adicional irrelevante extraída del modelo de clasificación.
 * Compartida entre ContenidoServiceImpl (v1.1) y ContenidoServiceImplV12.
 */
public final class StopWords {

    public static final Set<String> ESPANOL = Set.of(
            "el", "la", "los", "las", "un", "una", "unos", "unas", "del", "al",
            "de", "en", "con", "por", "para", "sin", "sobre", "entre", "desde", "hasta",
            "y", "o", "pero", "si", "que", "como", "cuando", "donde",
            "su", "sus", "esto", "esta", "este", "estos", "estas", "eso", "esa", "ese",
            "es", "son", "ser", "estar", "hay", "tiene", "puede", "permite",
            "utilizando", "utiliza", "usando", "usa", "creacion", "crear",
            "contenido", "texto", "material", "explica", "presenta", "muestra"
    );

    private StopWords() {
        // clase utilitaria, no instanciable
    }
}
