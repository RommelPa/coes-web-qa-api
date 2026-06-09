# COES Web QA API

API de preguntas y respuestas sobre la documentación pública de COES WebApi Mediciones.

La aplicación indexa la página:

```text
https://appserver.coes.org.pe/waMediciones/Help
```

y responde preguntas usando recuperación de texto con TF-IDF. No requiere API key.

## Opción 1: cargar imagen publicada desde GHCR

```bash
docker pull ghcr.io/rommelpa/coes-web-qa-api:latest
```

## Opción 2: construir imagen desde el repositorio

```bash
docker build -t coes-web-qa-api:local .
```

## Ejecutar la imagen

Si usas la imagen publicada en GHCR:

```bash
docker run --rm -p 8000:8000 ghcr.io/rommelpa/coes-web-qa-api:latest
```

Si construiste la imagen local:

```bash
docker run --rm -p 8000:8000 coes-web-qa-api:local
```

La API quedará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva estará en:

```text
http://127.0.0.1:8000/docs
```

## Ejemplo de entrada → respuesta

Entrada:

```json
{
  "question": "Que endpoint sirve para consultar demanda por fecha?",
  "top_k": 3
}
```

Prueba con Python:

```bash
python -c "import httpx; r=httpx.post('http://127.0.0.1:8000/ask', json={'question':'Que endpoint sirve para consultar demanda por fecha?','top_k':3}); print(r.status_code); print(r.json()['answer'][:250])"
```

Respuesta esperada:

```text
200
Según la documentación indexada de COES, la información más relevante encontrada es: Servicio Mediciones WebApi Introduction Servicio WebApi de información de Mediciones COES. Demanda Servicio que retorna información de demanda COES...
```

## Endpoints útiles

```text
GET  /health
GET  /metadata
POST /ask
GET  /metrics
```