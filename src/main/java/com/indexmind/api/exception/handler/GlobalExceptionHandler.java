package com.indexmind.api.exception.handler;

import com.indexmind.api.dto.CodigoError;
import com.indexmind.api.dto.ErrorDetail;
import com.indexmind.api.dto.ErrorResponse;
import com.indexmind.api.exception.ContenidoException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.time.Instant;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidacion (MethodArgumentNotValidException ex) {
        FieldError primerError = ex.getFieldErrors().get(0);
        String campo = primerError.getField();
        String mensaje = primerError.getDefaultMessage(); // el mensaje de tu anotación @Size/@NotBlank
        CodigoError error = mapearCodigo(campo, mensaje);

        var detalle = new ErrorDetail(error, mensaje, campo, Instant.now());
        return ResponseEntity.badRequest().body(new ErrorResponse(detalle));
    }

    @ExceptionHandler(ContenidoException.class)
    public ResponseEntity<ErrorResponse> handleContenidoException(ContenidoException ex) {
        var detalle = new ErrorDetail(ex.getCodigo(), ex.getMessage(), ex.getCampo(), Instant.now());

        HttpStatus status = switch (ex.getCodigo()) {
            case PREDICCION_RECHAZADA -> HttpStatus.UNPROCESSABLE_ENTITY;
            case ERROR_MODELO -> HttpStatus.INTERNAL_SERVER_ERROR;
            default -> HttpStatus.BAD_REQUEST;
        };

        return ResponseEntity.status(status).body(new  ErrorResponse(detalle));
    }

    private CodigoError getCodigo(String campo, String mensaje) {
        return mapearCodigo(campo, mensaje);
    }

    private CodigoError mapearCodigo(String campo, String mensaje){
        if(campo.equals("titulo")){
            return CodigoError.TITULO_MUY_LARGO;
        }
        if(mensaje.contains("no puede estar vacio")){
            return CodigoError.TEXTO_VACIO;
        }
        return CodigoError.TEXTO_MUY_LARGO;
    }
}
