package com.indexmind.api.util;

import java.text.Normalizer;
import java.util.regex.Pattern;

public final class TextUtils {

    private static final Pattern PATRON_ACENTOS = Pattern.compile("\\p{M}");

    public static String eliminarAcentos(String texto) {
        String textoDescompuesto = Normalizer.normalize(texto, Normalizer.Form.NFD);
        return PATRON_ACENTOS.matcher(textoDescompuesto).replaceAll("");
    }

    private TextUtils() {
    }
}