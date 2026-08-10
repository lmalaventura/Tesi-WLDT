# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste in linguaggio naturale
in chiamate REST verso il Persistence Service WLDT.

## Pipeline

```text
POST /query
   │
   ▼
OpenAPI
   │
   ▼
catalogo
   │
   ▼
selector top 3
   │
   ▼
prompt ristretto
   │
   ▼
Qwen3 8B / Ollama
   │
   ▼
GeneratedApiCall
   │
   ▼
validazione OpenAPI
   │
   ▼
preparazione HTTP
   │
   ▼
Persistence Service
```

## Requisiti

```text
Python >= 3.12
uv
Ollama
Qwen3 8B
```

## Configurazione predefinita

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=300

PERSISTENCE_SERVICE_BASE_URL=http://localhost:8081
OPENAPI_SPEC_URL=http://localhost:8081/openapi.yaml
REQUEST_TIMEOUT_SECONDS=120
```

## Avvio

Dalla directory:

```text
05_codice/agent_service
```

eseguire:

```powershell
uv run uvicorn app.main:app `
  --host 127.0.0.1 `
  --port 8000
```

## Endpoint

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

## Richiesta a `/query`

Esempio:

```json
{
  "query": "Mostrami lo snapshot del Digital Twin HDT-001"
}
```

## Structured output

Esempio di chiamata prodotta:

```json
{
  "method": "GET",
  "endpoint": "/hdts/{id}/snapshot",
  "pathParameters": {
    "id": "HDT-001"
  },
  "queryParameters": {},
  "body": null,
  "missingInformation": []
}
```

Il JSON Schema utilizzato da Ollama viene ristretto dinamicamente in funzione
delle operazioni candidate.

## Validazione

La chiamata non viene eseguita immediatamente dopo la generazione.

`ApiCallValidator` verifica la compatibilità con la specifica OpenAPI corrente.

Una chiamata non valida produce HTTP 502 e non raggiunge il Persistence
Service.

Non vengono effettuate correzioni automatiche post-hoc della chiamata.

## Errori principali

```text
422 — informazioni necessarie mancanti
502 — risposta LLM non utilizzabile o chiamata non valida
503 — OpenAPI, Ollama o Persistence Service non raggiungibile
```

## Test

```powershell
uv run python -m pytest -q
```

## Persistence Service simulato

Per il benchmark è disponibile:

```text
02_esperimenti/pipeline_finale/mock_persistence.py
```

Avvio dalla directory `05_codice/agent_service`:

```powershell
uv run uvicorn mock_persistence:app `
  --app-dir ..\..\02_esperimenti\pipeline_finale `
  --host 127.0.0.1 `
  --port 8081
```

## Configurazione locale del benchmark

```powershell
$env:PERSISTENCE_SERVICE_BASE_URL="http://127.0.0.1:8081"
$env:OPENAPI_SPEC_URL="http://127.0.0.1:8081/openapi.yaml"
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
$env:OLLAMA_MODEL="qwen3:8b"
$env:OLLAMA_TIMEOUT_SECONDS="300"

uv run uvicorn app.main:app `
  --host 127.0.0.1 `
  --port 8000
```

## Benchmark

Dalla root della repository:

```powershell
uv run --project .\05_codice\agent_service `
  python .\02_esperimenti\pipeline_finale\run_benchmark.py `
  --runs 3
```

Risultato congelato:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

## Limiti correnti

La pipeline è stata verificata contro un Persistence Service simulato.

Non sono ancora state completate:

- verifica sul sistema WLDT reale;
- integrazione nel Query Workbench;
- valutazione su un test set indipendente.

Il benchmark mostra inoltre che la conformità OpenAPI non garantisce da sola
la correttezza semantica della traduzione.