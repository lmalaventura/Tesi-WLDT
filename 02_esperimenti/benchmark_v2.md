# Benchmark v2 — casi di integrazione

Questo benchmark è stato definito dopo la verifica della specifica OpenAPI e
del comportamento richiesto dal Persistence Service.
La versione v2 corregge la ground truth utilizzata negli esperimenti iniziali
e costituisce la base dei casi successivamente utilizzati per la valutazione
della pipeline completa dell'Agent Service.

## Q1 — Elenco Digital Twin

Richiesta:

> Mostrami tutti i Digital Twin disponibili.

Chiamata attesa:

```text
GET /hdts
```

Non sono previsti path parameter, query parameter o request body.

## Q2 — Snapshot corrente

Richiesta:

> Mostrami il valore corrente delle proprietà del Digital Twin con id "HDT-001".

Chiamata attesa:

```text
GET /hdts/{id}/snapshot
```

Path parameter:

```text
id = HDT-001
```

L'endpoint deve rimanere espresso utilizzando il placeholder OpenAPI `{id}`.
Il valore concreto viene mantenuto separatamente nei path parameter.

## Q3 — Valori di una proprietà in un intervallo

Richiesta:

> Mostrami i valori della proprietà "heartRate" del Digital Twin "HDT-001"
> dal 1 luglio 2026 incluso all'8 luglio 2026 escluso.

Chiamata attesa:

```text
POST /query/event/values/valuesByName
```

Body:

```json
[
  {
    "hdtId": "HDT-001",
    "propertyName": "heartRate",
    "from": "2026-07-01T00:00:00Z",
    "to": "2026-07-08T00:00:00Z"
  }
]
```

Il request body ha come radice un array.

## Q4 — Confronto

Richiesta:

> Trova i Digital Twin che hanno almeno un'osservazione della proprietà
> "systolicPressure" maggiore di 150.

Chiamata attesa:

```text
POST /query/event/comparison
```

Body:

```json
{
  "comparisons": [
    {
      "propertyName": "systolicPressure",
      "comparison": "GT",
      "value": 150
    }
  ]
}
```

L'operatore atteso è `GT`, corrispondente strettamente a "maggiore di".

## Q5 — Statistiche senza filtri su HDT o modello

Richiesta:

> Calcola count, media, minimo e massimo della proprietà "heartRate" per tutti
> i Digital Twin dal 1 luglio 2026 incluso all'8 luglio 2026 escluso.

Chiamata attesa:

```text
POST /query/event/stats
```

Body:

```json
{
  "hdtIds": [],
  "modelIds": [],
  "modelNames": [],
  "propertyName": "heartRate",
  "from": "2026-07-01T00:00:00Z",
  "to": "2026-07-08T00:00:00Z"
}
```

Gli array `hdtIds`, `modelIds` e `modelNames` devono essere presenti.
Gli array vuoti rappresentano l'assenza del relativo filtro nella
configurazione considerata.

## Utilizzo nel benchmark controllato della pipeline

I cinque casi sono stati formalizzati nel file:

```text
02_esperimenti/pipeline_finale/cases.json
```

La ground truth del benchmark comprende:

- metodo HTTP;
- endpoint;
- path parameters;
- query parameters;
- request body;
- informazioni mancanti.

Il benchmark controllato della pipeline è stato eseguito il 10 agosto 2026
ripetendo i cinque casi tre volte, per un totale di 15 esecuzioni.
Il risultato congelato è:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

L'analisi aggregata è documentata in:

```text
03_risultati/benchmark_pipeline_finale.md
```

Questi casi sono stati utilizzati anche durante lo sviluppo e la diagnostica
della pipeline.
Il risultato deve quindi essere considerato un benchmark controllato e
regressivo e non un test set indipendente.