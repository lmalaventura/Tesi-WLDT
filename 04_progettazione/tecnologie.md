# Tecnologie adottate

## Python

L'Agent Service è implementato in Python.

Il progetto utilizza Python 3.12 o successivo.

La scelta permette di mantenere il componente indipendente dal frontend e dal
Persistence Service e di utilizzare librerie adatte all'integrazione con LLM,
HTTP e OpenAPI.

## FastAPI

FastAPI viene utilizzato per esporre l'Agent Service come microservizio HTTP.

Gli endpoint implementati sono:

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

## Pydantic

Pydantic viene utilizzato per:

- modelli request/response;
- rappresentazione di `GeneratedApiCall`;
- configurazione applicativa;
- produzione del JSON Schema di base dello structured output.

## HTTPX

HTTPX viene utilizzato per le comunicazioni HTTP con:

- Ollama;
- risorsa OpenAPI;
- Persistence Service.

## PyYAML

PyYAML viene utilizzato per il parsing della specifica OpenAPI in formato YAML.

## Ollama

Ollama viene utilizzato come runtime locale del modello linguistico.

La configurazione finale utilizza:

```text
qwen3:8b
```

La generazione utilizza:

```text
stream = false
think = false
temperature = 0
```

## Modelli analizzati

Durante la fase sperimentale sono stati analizzati:

- ChatGPT;
- Qwen3 4B;
- Qwen3 8B;
- Llama 3.1 8B.

Il confronto iniziale è stato utilizzato per analizzare il comportamento delle
diverse configurazioni e della rappresentazione del contesto OpenAPI.

Qwen3 8B è stato successivamente utilizzato nella pipeline locale finale.

## OpenAPI

La specifica analizzata utilizza:

```text
OpenAPI 3.1.1
```

e dichiara:

```text
info.version: v0.2.0
```

La specifica viene utilizzata per:

- catalogazione;
- selezione;
- costruzione del prompt;
- validazione.

## pytest

pytest viene utilizzato per i test automatici dell'Agent Service.

## uv

`uv` viene utilizzato per la gestione dell'ambiente Python, delle dipendenze e
per l'esecuzione dei comandi.

Esempio:

```powershell
uv run python -m pytest -q
```

## Pipeline dedicata

La soluzione finale non utilizza un framework agentico generalista.

La scelta non deriva dall'impossibilità di implementare il sistema con altri
framework, ma dalla natura circoscritta del flusso:

```text
selezione OpenAPI
→ generazione LLM
→ validazione
→ esecuzione REST
```

Una pipeline dedicata permette di mantenere esplicite le responsabilità dei
singoli componenti.