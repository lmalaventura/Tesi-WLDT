# Tesi WLDT — agente LLM per richieste NL → REST

Repository di lavoro della tesi dedicata alla traduzione di richieste espresse
in linguaggio naturale in chiamate REST verso il Persistence Service WLDT.

## Stato del progetto

È disponibile una prima implementazione completa dell'Agent Service.

La pipeline corrente esegue:

```text
richiesta naturale
→ caricamento OpenAPI
→ catalogo delle operazioni
→ selezione delle candidate
→ costruzione del prompt
→ Qwen3 8B tramite Ollama
→ output JSON strutturato
→ validazione OpenAPI
→ preparazione HTTP
→ esecuzione verso Persistence Service
→ risposta
```

L'implementazione corrente si trova in:

```text
05_codice/agent_service
```

La cartella:

```text
05_codice/agent
```

contiene invece il prototipo storico della fase sperimentale.

## Funzionalità implementate

L'Agent Service:

- recupera dinamicamente la specifica OpenAPI;
- costruisce un catalogo normalizzato;
- seleziona un massimo di tre candidate;
- costruisce un contesto ristretto;
- utilizza Qwen3 8B tramite Ollama;
- utilizza structured output;
- produce `GeneratedApiCall`;
- gestisce informazioni mancanti;
- valida la chiamata rispetto alla OpenAPI;
- prepara la richiesta HTTP;
- esegue la chiamata;
- restituisce la risposta del Persistence Service.

## Endpoint

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

## Struttura principale

```text
00_materiali/
01_appunti/
02_esperimenti/
03_risultati/
04_progettazione/
05_codice/
    agent/
    agent_service/
06_tesi/
```

## Tecnologie

```text
Python
FastAPI
Pydantic
HTTPX
PyYAML
Ollama
Qwen3 8B
pytest
uv
```

## Benchmark finale

La pipeline completa è stata verificata tramite un Persistence Service
simulato.

Il benchmark comprende:

```text
5 casi × 3 ripetizioni = 15 esecuzioni
```

Risultato congelato del 10/08/2026:

```text
Operation accuracy:      80%
Arguments accuracy:      60%
Semantic accuracy:       60%
Validation pass rate:    80%
Execution success rate:  80%
End-to-end success rate: 60%
Tempo medio:              25.731 s
```

Q2, Q3 e Q5 sono corretti in tutte le ripetizioni.

Q1 fallisce nella generazione dell'operazione e viene bloccato dal validatore.

Q4 seleziona l'endpoint corretto ma utilizza `GTE` invece di `GT`.

L'analisi completa è disponibile in:

```text
03_risultati/benchmark_pipeline_finale.md
```

Il risultato grezzo è:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
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

## Stato dell'integrazione WLDT

La pipeline è stata verificata end-to-end contro un Persistence Service
simulato.

Rimangono da completare:

- verifica contro il Persistence Service reale;
- integrazione nel Query Workbench;
- test end-to-end frontend → agent → persistence.

I risultati del benchmark corrente non vengono interpretati come stima
generale dell'accuratezza su richieste arbitrarie, perché i casi sono stati
utilizzati anche durante sviluppo e diagnostica.