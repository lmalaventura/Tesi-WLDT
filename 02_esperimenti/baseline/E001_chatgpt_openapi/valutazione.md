# Valutazione E001

## Obiettivo

Valutare la capacità di ChatGPT di leggere la specifica OpenAPI v0.2.0 e
individuare le operazioni rilevanti per l'interrogazione dei dati WLDT.

## Input

- file: `openapi.yaml`;
- modello: ChatGPT;
- data: 28/07/2026.

## Risultato

La risposta individua correttamente gli endpoint principali, tra cui:

- `GET /hdts`;
- `GET /hdts/{id}/properties`;
- `GET /hdts/{id}/observations`;
- `GET /hdts/{id}/snapshot`;
- `GET /hdts/{id}/snapshot/by-task`;
- `GET /properties/names`;
- `POST /query/event/values/valuesById`;
- `POST /query/event/values/valuesByName`;
- `POST /query/event/values/history`;
- `POST /query/event/comparison`;
- `POST /query/event/stats`;
- `POST /query/cohort`.

Sono descritti correttamente anche `PropertyValuesRequest`,
`PropertyStatsRequest`, `PropertiesByComparisonsRequestDto`, gli operatori di
confronto e la struttura `ComparisonSearchResult`. La risposta distingue le
informazioni esplicitamente presenti nel contratto dalle semantiche che non
possono essere ricavate con certezza, come il comportamento degli array vuoti
o i campi effettivamente richiesti dai tre endpoint `values`.

## Limiti

- I riferimenti alle righe del file e al nome `openapi(1).yaml` non sono stabili
  e non vanno riutilizzati nella documentazione finale.
- L'endpoint `/query/event/values/history` viene indicato come soluzione per lo
  storico sulla base del summary OpenAPI. L'analisi successiva del codice
  Kotlin ha mostrato che `from` e `to` non vengono applicati da questo route;
  tale informazione non era ricavabile dal solo contratto.

## Correzione della valutazione precedente

La prima versione di questo file classificava come inventati diversi endpoint
che sono invece presenti nell'OpenAPI e descriveva in modo errato lo schema di
`/query/event/comparison`. Quella valutazione era quindi non corretta ed è
stata sostituita durante il checkpoint del 03/08/2026.

## Esito

**CORRETTO CON LIMITI DEL CONTRATTO DOCUMENTATI**
