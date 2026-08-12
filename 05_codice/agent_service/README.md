# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste in linguaggio naturale
in chiamate REST verso il Persistence Service WLDT.

## Pipeline

```text
POST /query
    │
    ▼
OpenAPI corrente
    │
    ▼
catalogo delle operazioni
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
gestione missingInformation
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

`ApiCallValidator` verifica la compatibilità della chiamata con la specifica
OpenAPI corrente prima dell'esecuzione.
I controlli riguardano, quando applicabili:

- metodo ed endpoint;
- path parameter;
- query parameter;
- presenza del request body;
- struttura del body;
- campi obbligatori;
- tipi;
- valori enumerati;
- ulteriori vincoli specifici delle operazioni.

Una chiamata non valida produce HTTP 502 e non raggiunge il Persistence
Service.
Non vengono effettuate correzioni automatiche post-hoc della chiamata.

## Informazioni mancanti ed errori

Quando il modello segnala tramite `missingInformation` che la richiesta non
contiene dati necessari, l'elaborazione viene interrotta e l'Agent Service
restituisce HTTP 422. Gli errori principali sono:

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

Al checkpoint del 12/08/2026 la suite corrente comprende 46 test, completati
senza errori.

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

In questa configurazione l'Agent Service containerizzato raggiunge:

```text
Ollama
→ http://host.docker.internal:11434

Persistence Service
→ http://host.docker.internal:8081
```

Questa configurazione è stata verificata con successo utilizzando
`TEST-001`.

## Integrazione nello stack WLDT development

Nello stack Docker development l'Agent Service viene eseguito insieme a:

```text
mongodb
persistence-service
hdt-creation-service
whdt-monitor-frontend
```

La configurazione del servizio utilizza:

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

All'interno della rete Compose, Agent Service e Persistence Service comunicano
tramite il nome del servizio:

```text
http://persistence-service:8081
```

Ollama rimane invece in esecuzione sull'host Windows e viene raggiunto tramite:

```text
http://host.docker.internal:11434
```

## Verifica Docker-to-Docker

Il 12/08/2026 è stato verificato il seguente input:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

La pipeline ha prodotto:

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

Il Persistence Service ha restituito HTTP 200 con i valori memorizzati per
`TEST-001`.

Questo test verifica:

```text
Agent Service in Docker
→ Persistence Service in Docker
→ MongoDB
```

mentre Qwen3 8B viene raggiunto tramite Ollama sull'host.

## Integrazione con il Query Workbench

Il frontend WLDT è stato esteso introducendo una modalità:

```text
Natural Language
```

nel Query Workbench.
Il browser invia:

```text
POST /api/agent/query
```

a una Route Handler Next.js.
La Route Handler inoltra la richiesta server-side all'Agent Service attraverso:

```text
AGENT_SERVICE_URL=http://agent-service:8000
```

La soluzione finale evita quindi una chiamata diretta del browser al servizio
interno Docker.
Una prima integrazione basata su una rewrite automatica Next.js aveva prodotto
un errore `ECONNRESET / socket hang up` durante le richieste complete.
La comunicazione diretta dal container frontend all'Agent Service era invece
corretta. La rewrite dedicata è stata quindi sostituita da una Route Handler
esplicita.
Le modifiche frontend della tesi sono disponibili nel branch:

```text
lmalaventura/whdt-monitor-frontend
tesi/Natural-Language-Agent
```

## Verifica end-to-end dal browser

La modalità Natural Language è stata verificata utilizzando:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

Il Query Workbench ha mostrato:

```text
Method:       GET
Endpoint:     /hdts/{id}/snapshot
Validation:   valid
HTTP result:  200
```

e ha visualizzato nel browser i valori restituiti dal Persistence Service.
È stato quindi verificato il flusso:

```text
Browser
→ Query Workbench
→ Next.js Route Handler
→ Agent Service
→ Ollama / Qwen3 8B
→ validazione OpenAPI
→ Persistence Service
→ MongoDB
→ risultato nel browser
```

Questo test costituisce una verifica di integrazione sul sistema reale e non
sostituisce una valutazione quantitativa indipendente.

## Benchmark controllato

Per il benchmark controllato è disponibile un Persistence Service simulato:

```text
02_esperimenti/pipeline_finale/mock_persistence.py
```

Il benchmark può essere eseguito dalla root della repository con:

```powershell
uv run --project .\05_codice\agent_service `
  python .\02_esperimenti\pipeline_finale\run_benchmark.py `
  --runs 3
```

Il risultato congelato del 10/08/2026 è:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

Il benchmark utilizza un Persistence Service simulato e rimane separato dai
successivi smoke test sul sistema WLDT reale.
I risultati congelati non vengono modificati retroattivamente sulla base delle
successive attività di integrazione.

## Stato corrente

Al checkpoint del 12/08/2026 sono state completate:

- pipeline NL-to-REST;
- selezione deterministica top 3;
- integrazione con Qwen3 8B tramite Ollama;
- structured output;
- gestione delle informazioni mancanti;
- validazione OpenAPI;
- preparazione ed esecuzione della richiesta HTTP;
- test automatici;
- benchmark controllato;
- verifica contro il Persistence Service WLDT reale;
- containerizzazione dell'Agent Service;
- integrazione nello stack Docker development;
- comunicazione Docker-to-Docker;
- integrazione della modalità Natural Language nel Query Workbench;
- verifica end-to-end dal browser.

Rimangono aperte principalmente:

- valutazione su un test set indipendente;
- eventuali modifiche richieste durante la revisione;
- utilizzo dei risultati nella stesura definitiva della tesi.