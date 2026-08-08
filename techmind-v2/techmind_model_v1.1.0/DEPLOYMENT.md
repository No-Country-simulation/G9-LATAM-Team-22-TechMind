# Despliegue de TechMind con Docker

Esta guía describe cómo ejecutar la API REST de TechMind dentro de un
contenedor Docker.

## Requisitos

- Docker con soporte para contenedores Linux.
- Docker Compose para la ejecución mediante `docker compose`.
- Puerto local disponible, por defecto `8000`.

## Construir la imagen

Desde el directorio raíz del paquete:

```bash
docker build -t techmind-api:1.0.0 .
```

## Ejecutar el contenedor

```bash
docker run --rm \
  --name techmind-api \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -p 127.0.0.1:8000:8000 \
  techmind-api:1.0.0
```

## Ejecutar mediante Docker Compose

```bash
docker compose up --build
```

Para ejecutar en segundo plano:

```bash
docker compose up --build -d
```

Para detener y eliminar el contenedor:

```bash
docker compose down
```

## Verificar la API

Health check:

```text
http://127.0.0.1:8000/health
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

## Ejemplo de solicitud

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"textos":["python pandas machine learning predictive model"]}'
```

## Variables disponibles

- `TECHMIND_API_PORT`: puerto local publicado por Docker Compose.
- `TECHMIND_IMAGE_NAME`: nombre de la imagen.
- `TECHMIND_IMAGE_TAG`: etiqueta de la imagen.
- `TECHMIND_CONTAINER_NAME`: nombre del contenedor.

Ejemplo:

```bash
TECHMIND_API_PORT=8080 docker compose up --build
```

## Seguridad

La configuración incluida:

- Ejecuta la aplicación como usuario sin privilegios.
- Elimina todas las capacidades Linux.
- Impide la adquisición de nuevos privilegios.
- Utiliza un sistema de archivos de solo lectura con `/tmp` temporal.
- Publica el puerto únicamente en `127.0.0.1`.

Para un despliegue público todavía deben añadirse autenticación, HTTPS,
control de acceso, limitación de solicitudes, registro centralizado y
gestión externa de secretos.

## Integridad del modelo

SHA-256 esperado:

```text
488ec7d47f7697f870fde6877d8df54e5ce1fedbc29842dd669a1014c7715cfb
```
