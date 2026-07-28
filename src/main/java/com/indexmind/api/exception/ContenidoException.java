package com.indexmind.api.exception;

import com.indexmind.api.dto.CodigoError;

public class ContenidoException extends RuntimeException {
    private final CodigoError codigo;
    private final String campo;
    public ContenidoException(String message, CodigoError error, String campo) {
        super(message);
        this.codigo = error;
        this.campo = campo;
    }

    public CodigoError getCodigo() {
        return codigo;
    }
    public String getCampo() {
        return campo;
    }
}
