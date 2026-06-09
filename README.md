# COES Web QA API

API de preguntas y respuestas sobre la documentación pública de **COES WebApi Mediciones**.

## Fuente indexada

Sitio web usado como fuente:

```text
https://appserver.coes.org.pe/waMediciones/Help
```

Índice generado:

```text
24 páginas
123 fragmentos de texto
```

## Endpoints

| Método | Endpoint    | Descripción                                  |
| ------ | ----------- | -------------------------------------------- |
| GET    | `/`         | Información básica del servicio              |
| GET    | `/health`   | Verifica si la API está activa               |
| GET    | `/metadata` | Muestra metadatos del índice                 |
| POST   | `/ask`      | Recibe una pregunta y devuelve una respuesta |
| GET    | `/metrics`  | Métricas en formato tipo Prometheus          |

## Construir la imagen Docker

Desde la raíz del proyecto:

```bash
docker build -t coes-web-qa-api:local .
```

## Ejecutar el contenedor

```bash
docker run --rm -p 8000:8000 coes-web-qa-api:local
```

La API quedará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI estará en:

```text
http://127.0.0.1:8000/docs
```

## Ejemplo de entrada

Archivo `examples/request.json`:

```json
{
  "question": "Que endpoint sirve para consultar demanda por fecha?",
  "top_k": 3
}
```

## Probar la API con PowerShell

Con el contenedor en ejecución:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/ask" `
  -ContentType "application/json" `
  -InFile examples/request.json
```

## Probar la API con Python

```powershell
uv run python -c "import httpx; r=httpx.post('http://127.0.0.1:8000/ask', json={'question':'Que endpoint sirve para consultar demanda por fecha?','top_k':3}); print(r.status_code); print(r.json()['answer'][:250])"
```

## Ejemplo de respuesta

```text
Según la documentación indexada de COES, la información más relevante encontrada es: Servicio Mediciones WebApi Introduction Servicio WebApi de información de Mediciones COES...
```

La respuesta completa incluye:

* `answer`: respuesta generada a partir del contenido indexado.
* `confidence`: nivel de confianza aproximado.
* `sources`: fragmentos de documentación usados como evidencia.

## Validar endpoints básicos

Con el contenedor en ejecución:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/metadata
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

Respuesta esperada de `/health`:

```json
{
  "status": "ok"
}
```

La respuesta de `/metadata` debe incluir:

```text
page_count: 24
chunk_count: 123
```

## Desarrollo local

Instalar dependencias:

```bash
uv sync --dev
```

Reconstruir el índice local:

```bash
uv run python -m scripts.build_index
```

Ejecutar la API localmente:

```bash
uv run uvicorn app.main:app --reload
```

Ejecutar tests:

```bash
uv run pytest
```

Ejecutar lint:

```bash
uv run ruff check .
```