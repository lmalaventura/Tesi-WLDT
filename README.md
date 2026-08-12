# Tesi WLDT — agente LLM per richieste NL → REST

Repository di lavoro della tesi dedicata alla traduzione di richieste espresse
in linguaggio naturale in chiamate REST verso il Persistence Service WLDT.

## Obiettivo

Il progetto introduce nel sistema WLDT un Agent Service capace di ricevere una
richiesta in linguaggio naturale, individuare le operazioni compatibili con il
contratto OpenAPI corrente, utilizzare un modello linguistico per proporre una
chiamata REST e validarla prima dell'esecuzione.

Il modello linguistico non interagisce direttamente con il Persistence Service.
La generazione viene inserita in una pipeline che mantiene separate:

```text
interpretazione della richiesta
→ controllo deterministico
→ esecuzione REST
```

## Stato del progetto

Al checkpoint del 12/08/2026 lo scope funzionale principale
dell'implementazione è completato.

La pipeline corrente è:

```text
richiesta naturale
→ caricamento dinamico OpenAPI
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

L'Agent Service è stato inoltre:

- verificato contro il Persistence Service WLDT reale;
- containerizzato;
- inserito nello stack Docker development;
- integrato nel Query Workbench;
- verificato con un flusso end-to-end dal browser al Persistence Service.

L'implementazione corrente dell'agente si trova in:

```text
05_codice/agent_service
```

La directory:

```text
05_codice/agent
```

contiene invece il prototipo storico utilizzato durante le prime fasi
sperimentali.

## Architettura integrata

Il flusso verificato è:

```text
Utente
  ↓
Query Workbench
  ↓
Natural Language
  ↓
Next.js Route Handler
  ↓
Agent Service
  ↓
  ├──→ Ollama / Qwen3 8B
  │
  └──→ Persistence Service
              ↓
            MongoDB
  ↓
risultato nel frontend
```

Il browser invia la richiesta al frontend Next.js tramite:

```text
POST /api/agent/query
```

La Route Handler server-side inoltra quindi la richiesta all'Agent Service
all'interno della rete Docker.

## Funzionalità principali

L'Agent Service:

- recupera dinamicamente la specifica OpenAPI;
- costruisce un catalogo normalizzato delle operazioni;
- seleziona un massimo di tre candidate;
- costruisce un contesto ristretto per il modello;
- utilizza Qwen3 8B tramite Ollama;
- richiede un output strutturato;
- produce una struttura `GeneratedApiCall`;
- gestisce le informazioni mancanti;
- valida la chiamata rispetto alla OpenAPI corrente;
- prepara la richiesta HTTP;
- esegue la chiamata sul Persistence Service;
- restituisce il risultato al client.

## Endpoint dell'Agent Service

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

## Struttura principale della repository

```text
00_materiali/       specifiche e riferimenti esterni
01_appunti/         diario e decisioni tecniche
02_esperimenti/     benchmark ed evidenze sperimentali
03_risultati/       metodologia e risultati aggregati
04_progettazione/   documentazione progettuale
05_codice/          prototipo storico e Agent Service corrente
06_tesi/            struttura e bozze per la stesura
docs/               documentazione tecnica complessiva
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
Docker
Docker Compose
Next.js
TypeScript
```

## Test automatici

Dalla directory:

```text
05_codice/agent_service
```

è possibile eseguire:

```powershell
uv run python -m pytest -q
```

Al checkpoint del 12/08/2026 la suite corrente comprende 46 test e viene
completata senza errori.

## Benchmark controllato della pipeline

La pipeline completa è stata verificata tramite un Persistence Service
simulato in un benchmark controllato composto da:

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

Q2, Q3 e Q5 risultano corretti in tutte le ripetizioni.

Q1 produce una scelta errata dell'operazione, che viene successivamente
bloccata dal validatore.

Q4 seleziona un'operazione compatibile con la OpenAPI ma utilizza `GTE`
invece di `GT`, mostrando che la conformità strutturale non implica
necessariamente equivalenza semantica con la richiesta dell'utente.

L'analisi completa è disponibile in:

```text
03_risultati/benchmark_pipeline_finale.md
```

Il risultato congelato è:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

I cinque casi del benchmark sono stati utilizzati anche durante lo sviluppo e
la diagnostica. Il risultato viene quindi interpretato come benchmark
controllato e regressivo della pipeline, non come stima generale
dell'accuratezza su richieste arbitrarie.

## OpenAPI degli esperimenti e OpenAPI runtime

La copia:

```text
00_materiali/openapi.yaml
```

rappresenta la specifica utilizzata dagli esperimenti e dal benchmark
controllato del 10/08/2026.

Durante la successiva integrazione con il Persistence Service reale è stata
recuperata dinamicamente la specifica esposta dal servizio in esecuzione.

I risultati sperimentali congelati non vengono modificati retroattivamente in
funzione delle successive evoluzioni della specifica o del sistema WLDT.

## Verifica sul sistema WLDT reale

L'Agent Service è stato verificato sullo stack WLDT reale utilizzando un
Digital Twin di test con identificatore:

```text
TEST-001
```

Una richiesta naturale relativa allo snapshot corrente ha prodotto:

```text
GET /hdts/{id}/snapshot
id = TEST-001
```

La chiamata ha superato la validazione, è stata eseguita sul Persistence
Service e ha restituito HTTP 200 con i valori memorizzati nel sistema.

La stessa pipeline è stata successivamente verificata dal Query Workbench del
frontend, completando il flusso:

```text
browser
→ frontend
→ Agent Service
→ Persistence Service
→ MongoDB
→ frontend
```

Questa verifica costituisce uno smoke test di integrazione e rimane distinta
dal benchmark quantitativo controllato.

## Stato successivo

Le principali attività ancora aperte riguardano:

- valutazione su un insieme di richieste indipendente dai casi utilizzati
  durante lo sviluppo;
- eventuali modifiche richieste;
- stesura definitiva della tesi;
- discussione finale dei risultati e dei limiti.

L'implementazione funzionale principale viene considerata congelata al
12/08/2026 salvo correzioni o richieste successive.