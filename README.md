# 🚀 IndexMind — Documentación del Proyecto

## 📝 1. Introducción
**IndexMind** es una solución orientada a la organización inteligente de contenido técnico mediante técnicas avanzadas de Ciencia de Datos. Su propósito principal es facilitar la clasificación, consulta y reutilización de información proveniente de documentos, artículos, cursos, tutoriales y otros materiales de referencia técnica que consumen estudiantes, profesionales y comunidades tecnológicas.

### ⚠️ El Problema
Actualmente, el gran volumen de información técnica dificulta la organización y reutilización eficiente del conocimiento. Encontrar datos relevantes de forma rápida y mantener una base de conocimiento estructurada representa un desafío crítico dentro del área tecnológica. Esta problemática es el punto de partida del proyecto.

---

## 🎯 2. Objetivos y Validación del Mercado
Las herramientas orientadas a la gestión del conocimiento son clave para organizaciones, instituciones educativas y equipos de desarrollo. Automatizar de forma inteligente la organización de este contenido técnico permite:

* **Optimización de Tiempo:** Reducir significativamente el tiempo invertido en localizar información clave.
* **Productividad:** Mejorar el rendimiento global en el desarrollo de software y tareas de investigación.
* **Colaboración:** Facilitar el flujo y el intercambio de conocimiento interdepartamental.
* **Aprendizaje Continuo:** Apoyar de manera ágil los procesos de capacitación técnica interna.
* **Escalabilidad:** Crecer repositorios de conocimiento institucionales de forma eficiente y ordenada.

---

## 🧱 3. Arquitectura del Sistema
El sistema implementa una arquitectura desacoplada basada en microservicios y consumo de APIs REST. El flujo de datos se procesa de la siguiente manera:

1. El sistema recibe el contenido técnico proporcionado por el usuario mediante solicitudes **HTTP** con payloads en formato **JSON**.
2. Los datos son direccionados al **Microservicio de Ciencia de Datos** para su procesamiento lingüístico y extracción.
3. El microservicio devuelve una respuesta estructurada en formato **JSON** con las clasificaciones y metadatos obtenidos.
4. Los resultados se entregan de vuelta al cliente final a través de la **API REST**.

---

## 🛠️ 4. Stack Tecnológico

### 💻 Backend
* **Lenguaje:** Java 17
* **Framework:** Spring Boot
* **Gestor de Dependencias:** Maven
* **IDE Recomendado:** IntelliJ IDEA
* **Librerías y Dependencias:**
    * Spring Web: Creación de endpoints RESTful y manejo de peticiones HTTP.
    * Spring Validation: Validación declarativa de datos de entrada en solicitudes JSON.
    * SpringDoc OpenAPI (v2.5.0): Generación automática de especificación OpenAPI 3.0 y documentación interactiva mediante Swagger UI.
    * Lombok: Reducción de código repetitivo (Getters, Setters, Constructor).
    * Spring Boot DevTools: Recarga rápida en entorno de desarrollo.

### 🧪 Data Science
* **Procesamiento de Lenguaje Natural (NLP):** SpaCy
* **Análisis de Datos:** Pandas
* **Machine Learning:** Scikit-Learn
* **Entornos de Desarrollo:** Jupyter Notebooks & Visual Studio Code

---
## 📂 5. Organización del Backend
Actualmente el Backend se encuentra organizado de la siguiente manera:
```
src
└── main
    └── java
        └── com.indexmind.api
            ├── controller
            ├── dto
            ├── service
            ├── client
            ├── exception
            │   └── handler
            └── config
```
---
## 📡 6. API REST
Actualmente la API implementa los siguientes endpoints.
### GET /api/v1/health

Permite verificar el estado del servicio.

#### Respuesta exitosa (200)

```json
{
    "status": "ok",
    "modelo_cargado": true,
    "version": "1.0"
}
```

#### Modelo no disponible (503)

```json
{
    "status": "error",
    "modelo_cargado": false,
    "version": "1.0"
}
```

---

### POST /api/v1/contenido

Recibe un contenido técnico para ser clasificado.

#### Request

```json
{
    "titulo": "Introducción a Spring Boot",
    "texto": "Spring Boot facilita el desarrollo de aplicaciones Java..."
}
```

#### Response

```json
{
    "categoria": "Backend",
    "probabilidad": 0.89,
    "informacion_adicional": [
        "Java",
        "Spring Boot",
        "API REST"
    ]
}
```
