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

La chiamata generata dal modello non viene inviata direttamente al backend.

Prima dell'esecuzione viene verificata deterministicamente rispetto alla
specifica OpenAPI corrente.

## Requisiti

Per l'esecuzione locale:

```text
Python >= 3.12
uv
Ollama
Qwen3 8B
```

Per l'esecuzione containerizzata:

```text
Docker
Docker Compose
Ollama sull'host
Qwen3 8B
```

## Configurazione predefinita

I valori predefiniti sono:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=300

PERSISTENCE_SERVICE_BASE_URL=http://localhost:8081
OPENAPI_SPEC_URL=http://localhost:8081/openapi.yaml
REQUEST_TIMEOUT_SECONDS=120
```

I valori possono essere sovrascritti tramite variabili d'ambiente.

## Avvio locale

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

Il servizio è quindi disponibile su:

```text
http://127.0.0.1:8000
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
  "query": "Mostrami lo snapshot del Digital Twin TEST-001"
}
```

## Structured output

Esempio di chiamata prodotta:

```json
{
  "method": "GET",
  "endpoint": "/hdts/{id}/snapshot",
  "pathParameters": {
    "id": "TEST-001"
  },
  "queryParameters": {},
  "body": null,
  "missingInformation": []
}
```

Il JSON Schema utilizzato da Ollama viene ristretto dinamicamente in funzione
delle operazioni candidate.

Il placeholder OpenAPI rimane nell'endpoint:

```text
/hdts/{id}/snapshot
```

mentre il valore concreto viene mantenuto separatamente in:

```text
pathParameters.id
```

La sostituzione avviene soltanto durante la preparazione della richiesta HTTP.

## Validazione

La chiamata non viene eseguita immediatamente dopo la generazione.

`ApiCallValidator` verifica la compatibilità con la specifica OpenAPI corrente.

I controlli riguardano, quando applicabili:

- metodo ed endpoint;
- path parameter;
- query parameter;
- presenza del request body;
- struttura del body;
- campi obbligatori;
- tipi;
- enum;
- ulteriori vincoli specifici delle operazioni.

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

Dalla directory:

```text
05_codice/agent_service
```

eseguire:

```powershell
uv run python -m pytest -q
```

## Docker

L'Agent Service dispone di un `Dockerfile` nella directory:

```text
05_codice/agent_service
```

L'immagine può essere costruita manualmente con:

```powershell
docker build -t wldt-agent-service:dev .
```

### Esecuzione standalone

Per verificare il container separatamente dallo stack Compose è possibile
raggiungere Ollama e Persistence Service attraverso l'host Docker Desktop:

```powershell
docker run -d `
  --name wldt-agent-service-test `
  -p 8000:8000 `
  -e OLLAMA_BASE_URL="http://host.docker.internal:11434" `
  -e OLLAMA_MODEL="qwen3:8b" `
  -e OLLAMA_TIMEOUT_SECONDS="300" `
  -e PERSISTENCE_SERVICE_BASE_URL="http://host.docker.internal:8081" `
  -e OPENAPI_SPEC_URL="http://host.docker.internal:8081/openapi.yaml" `
  -e REQUEST_TIMEOUT_SECONDS="120" `
  wldt-agent-service:dev
```

In questa configurazione:

```text
Agent Service container
        ↓
host.docker.internal:11434
        ↓
Ollama sull'host
```

e:

```text
Agent Service container
        ↓
host.docker.internal:8081
        ↓
Persistence Service
```

Questa configurazione è stata verificata con successo utilizzando
`TEST-001`.

## Integrazione nello stack WLDT development

Nell'ambiente WLDT development l'Agent Service viene aggiunto al progetto
Docker Compose insieme a:

```text
mongodb
persistence-service
hdt-creation-service
whdt-monitor-frontend
```

La configurazione utilizzata per il servizio è:

```yaml
agent-service:
  build:
    context: ../../Tesi-WLDT/05_codice/agent_service
  restart: unless-stopped
  environment:
    OLLAMA_BASE_URL: "http://host.docker.internal:11434"
    OLLAMA_MODEL: "qwen3:8b"
    OLLAMA_TIMEOUT_SECONDS: "300"
    PERSISTENCE_SERVICE_BASE_URL: "http://persistence-service:8081"
    OPENAPI_SPEC_URL: "http://persistence-service:8081/openapi.yaml"
    REQUEST_TIMEOUT_SECONDS: "120"
  ports:
    - "8000:8000"
  depends_on:
    persistence-service:
      condition: service_started
```

In questa configurazione il Persistence Service non viene raggiunto passando
dalla porta dell'host.

Agent Service e Persistence Service appartengono alla stessa rete Compose e la
comunicazione utilizza il nome del servizio:

```text
http://persistence-service:8081
```

Ollama rimane invece in esecuzione sull'host Windows e viene raggiunto tramite:

```text
http://host.docker.internal:11434
```

La configurazione risultante è quindi:

```text
client
   ↓
agent-service:8000
   ↓
   ├──→ host.docker.internal:11434 → Ollama / Qwen3 8B
   │
   └──→ persistence-service:8081
                 ↓
              MongoDB
```

## Verifica Docker-to-Docker

Il 12 agosto 2026 è stato verificato il seguente input:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

Il modello ha prodotto:

```text
GET /hdts/{id}/snapshot
id = TEST-001
```

La validazione ha restituito:

```text
valid = true
```

e la richiesta preparata è stata:

```text
GET http://persistence-service:8081/hdts/TEST-001/snapshot
```

Il Persistence Service ha restituito HTTP 200 con:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

Questo test verifica la comunicazione:

```text
Agent Service in Docker
→ Persistence Service in Docker
→ MongoDB
```

mentre il modello Qwen3 8B viene raggiunto tramite Ollama sull'host.

## Persistence Service simulato

Per il benchmark controllato è disponibile:

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

Il benchmark del 10 agosto 2026 utilizza un Persistence Service simulato e
rimane separato dai successivi smoke test sul sistema WLDT reale.

I risultati congelati non vengono modificati retroattivamente sulla base delle
successive attività di integrazione.

## Stato corrente

Sono state completate:

- pipeline NL-to-REST;
- selezione deterministica top 3;
- integrazione con Qwen3 8B tramite Ollama;
- structured output;
- validazione OpenAPI;
- preparazione della richiesta HTTP;
- esecuzione sul Persistence Service;
- test automatici;
- benchmark controllato con Persistence Service simulato;
- verifica dell'Agent Service contro il Persistence Service WLDT reale;
- containerizzazione dell'Agent Service;
- verifica standalone del container;
- integrazione nello stack Docker development;
- comunicazione Docker-to-Docker con il Persistence Service.

Rimangono da completare:

- integrazione della modalità Natural Language nel Query Workbench;
- valutazione su un test set indipendente;
- eventuale evoluzione della metodologia di valutazione sulla base dei
  successivi feedback del relatore.

Il benchmark ha inoltre evidenziato che la conformità OpenAPI non garantisce da
sola la correttezza semantica della traduzione.