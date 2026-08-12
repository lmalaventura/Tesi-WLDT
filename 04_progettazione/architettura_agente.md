# Architettura dell'Agent Service

## Obiettivo

L'Agent Service è un componente indipendente incaricato di tradurre richieste
espresse in linguaggio naturale in chiamate REST compatibili con il
Persistence Service WLDT.
L'agente non modifica il Persistence Service e utilizza la specifica OpenAPI
corrente come contratto per individuare, generare e validare le operazioni
disponibili.

## Architettura generale

```text
Utente / Client
      │
      ▼
POST /query
      │
      ▼
OpenApiLoader
      │
      ▼
OpenApiCatalog
      │
      ▼
ApiSelector
(top 3)
      │
      ▼
PromptBuilder
      │
      ▼
Ollama / Qwen3 8B
      │
      ▼
GeneratedApiCall
      │
      ├── missingInformation
      │        └──► HTTP 422
      │
      ▼
ApiCallValidator
      │
      ├── chiamata non valida
      │        └──► HTTP 502
      │
      ▼
ApiRequestPreparer
      │
      ▼
RestClient
      │
      ▼
Persistence Service
      │
      ▼
Risposta
```

## Interfaccia HTTP

L'Agent Service è implementato tramite FastAPI.
Espone:

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

`POST /query` rappresenta il punto di ingresso della pipeline completa.

## Caricamento della OpenAPI

`OpenApiLoader` recupera la specifica dall'indirizzo configurato del
Persistence Service.
La pipeline operativa non utilizza una copia statica della OpenAPI come fonte
principale.
Il documento viene analizzato prima di procedere alle fasi successive.

## Catalogo delle operazioni

`OpenApiCatalog` trasforma il documento OpenAPI in una rappresentazione
normalizzata delle operazioni disponibili.
Per ogni operazione vengono mantenute informazioni quali:

- metodo HTTP;
- path;
- operationId;
- summary;
- description;
- tag;
- path parameter obbligatori;
- query parameter obbligatori;
- presenza di request body.

Il catalogo permette al selettore di lavorare su una rappresentazione più
compatta della specifica.

## Selezione delle candidate

`ApiSelector` confronta deterministicamente la richiesta dell'utente con i
metadati delle operazioni.
La pipeline seleziona un massimo di tre candidate ordinate per punteggio.
La selezione riduce il numero di operazioni che devono essere interpretate dal
modello.

## Costruzione del prompt

`PromptBuilder` riceve:

- richiesta naturale;
- candidate ordinate;
- documento OpenAPI corrente.

Il prompt contiene soltanto le informazioni OpenAPI necessarie alle candidate e
gli schemi referenziati rilevanti.
Tra le regole inserite nel prompt:

- utilizzare una delle candidate;
- mantenere il path OpenAPI nella forma originale;
- mantenere separati i valori dei path parameter;
- rispettare la struttura radice del body;
- distinguere `propertyName` e `propertyId`;
- non inventare informazioni mancanti.

## Structured output

Il modello produce una struttura `GeneratedApiCall`.
Lo schema di output viene ristretto dinamicamente sulla base delle candidate.
Possono essere vincolati:

- metodo HTTP;
- endpoint;
- tipo radice del body;
- campi obbligatori;
- requisiti specifici dell'operazione.

## Modello linguistico

La configurazione finale utilizza:

```text
Qwen3 8B
```

tramite Ollama.
La generazione utilizza structured output con:

```text
stream = false
think = false
temperature = 0
```

## Informazioni mancanti

`GeneratedApiCall` contiene:

```text
missingInformation
```

Se sono presenti informazioni necessarie non determinabili dalla richiesta, la
pipeline interrompe l'esecuzione e restituisce HTTP 422.

## Validazione

`ApiCallValidator` verifica deterministicamente la chiamata generata rispetto
alla OpenAPI corrente.
Una chiamata non valida viene rifiutata prima dell'esecuzione.
Il validatore non corregge automaticamente la chiamata generata.

## Preparazione della richiesta

Dopo la validazione, `ApiRequestPreparer` costruisce la richiesta HTTP concreta.
La fase comprende:

- sostituzione dei placeholder del path;
- costruzione dell'URL;
- gestione dei query parameter;
- mantenimento del request body.

## Esecuzione

`RestClient` esegue la richiesta verso il Persistence Service.
La risposta del backend viene quindi restituita dall'Agent Service insieme alle
informazioni necessarie a descrivere l'esito della pipeline.

## Motivazione della pipeline

Gli esperimenti preliminari hanno mostrato difficoltà dei modelli locali quando
ricevono direttamente un contesto OpenAPI troppo ampio.
La pipeline finale separa quindi:

```text
selezione deterministica
        ↓
generazione LLM
        ↓
validazione deterministica
        ↓
esecuzione REST
```

Il modello non costituisce l'unico livello responsabile della correttezza
dell'interazione.

## Limite emerso dal benchmark

Il benchmark controllato della pipeline ha mostrato che la validità OpenAPI
non garantisce automaticamente la correttezza semantica.
Nel caso Q4 il modello produce un operatore `GTE`, valido secondo OpenAPI, per
una richiesta che richiede semanticamente `GT`.
Validazione strutturale e correttezza semantica vengono quindi considerate due
proprietà differenti.