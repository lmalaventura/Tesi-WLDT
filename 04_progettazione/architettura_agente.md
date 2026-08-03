# Architettura dell'Agent Service

## Obiettivo

Realizzare un servizio capace di tradurre richieste in linguaggio naturale in
chiamate REST valide per il Persistence Service WLDT, eseguirle e inoltrare il
risultato al client.

L'Agent Service si adatta all'infrastruttura esistente. Il Persistence Service
resta la fonte di verità per le operazioni disponibili e non deve incorporare
logica LLM.

## Flusso generale

```text
Client
  │ richiesta naturale + eventuale contesto
  ▼
Agent Service
  │
  ├─ OpenApiProvider ───────► GET /openapi.yaml
  │                           Persistence Service
  │
  ├─ ApiCatalog / ApiSelector
  ├─ PromptBuilder
  ├─ OllamaClient ──────────► Ollama
  ├─ OutputParser
  ├─ ApiCallValidator
  ├─ RestExecutor ──────────► Persistence Service
  └─ ResponseMapper
  │
  ▼
Client
```

## Componenti

### OpenApiProvider

Recupera la specifica da `GET /openapi.yaml` del Persistence Service. La
specifica può essere conservata in cache, ma deve essere prevista una politica
di aggiornamento e la gestione dell'indisponibilità del backend.

La stessa versione deve alimentare sia il catalogo delle operazioni sia la
validazione, evitando divergenze tra generazione ed esecuzione.

### ApiCatalog

Trasforma la sezione `paths` della specifica in una rappresentazione interna
contenente almeno:

- metodo HTTP;
- path template;
- descrizione o summary;
- parametri per path e query;
- schema del request body;
- campi obbligatori.

### ApiSelector

Riceve la richiesta naturale e seleziona un insieme ristretto di operazioni
candidate. Il prototipo usa regole lessicali manuali; la versione integrata
dovrà costruire il catalogo dalla OpenAPI e separare le regole di dominio dal
codice di orchestrazione.

### PromptBuilder

Fornisce al modello soltanto le operazioni candidate e le informazioni
necessarie per costruire la chiamata. Impone un output JSON strutturato e vieta
l'invenzione di endpoint o campi.

### OllamaClient

Invia il prompt al modello locale tramite l'API HTTP di Ollama. Il modello
iniziale del prototipo è Qwen3 8B; la configurazione deve rimanere esterna al
codice.

### OutputParser

Verifica che la risposta sia un oggetto JSON e la converte nel modello interno
della chiamata API.

### ApiCallValidator

Confronta la chiamata generata con la OpenAPI corrente. Controlla la coppia
metodo/path, i parametri, il body e le informazioni mancanti. Una chiamata non
valida o incompleta non viene eseguita.

### RestExecutor

Risolti i path parameter e costruita la query string, esegue la richiesta sul
Persistence Service rispettando timeout e gestione degli errori.

### ResponseMapper

Restituisce al client uno dei seguenti esiti:

- successo con chiamata generata e dati del Persistence Service;
- informazioni mancanti;
- errore di generazione o validazione;
- errore del Persistence Service.

## Decisioni progettuali

Il modello non riceve l'intera OpenAPI. La specifica completa viene elaborata
dal servizio, mentre nel prompt entrano soltanto le operazioni candidate. La
scelta deriva dagli esperimenti diagnostici E007 ed E008, nei quali Qwen3 8B
ha selezionato correttamente i path presentati in forma isolata o sintetica.
Poiché si tratta di esecuzioni singole, questo risultato è considerato una
motivazione progettuale preliminare e non una prova statistica.

Il flusso resta deterministico: l'LLM propone una sola chiamata e non può
eseguirla direttamente. La validazione applicativa precede sempre l'accesso al
Persistence Service.
