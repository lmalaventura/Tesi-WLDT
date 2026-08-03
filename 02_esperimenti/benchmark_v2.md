# Benchmark v2 — casi per l'integrazione

Versione proposta dopo la verifica congiunta di OpenAPI e implementazione del
Persistence Service. Non è ancora stata utilizzata per i benchmark dei
modelli.

## Q1 — Elenco Digital Twin

Mostrami tutti i Digital Twin disponibili.

Atteso: `GET /hdts`.

## Q2 — Snapshot corrente

Mostrami il valore corrente delle proprietà del Digital Twin con id "HDT-001".

Atteso: `GET /hdts/{id}/snapshot`, con `id = HDT-001`.

## Q3 — Storico in un intervallo

Mostrami i valori della proprietà "heartRate" del Digital Twin "HDT-001" dal
1 luglio 2026 incluso all'8 luglio 2026 escluso.

Atteso: `POST /query/event/values/valuesByName`, body array con `hdtId`,
`propertyName`, `from` e `to`.

## Q4 — Confronto

Trova i Digital Twin che hanno almeno un'osservazione della proprietà
"systolicPressure" maggiore di 150.

Atteso: `POST /query/event/comparison` con operatore `GT`.

## Q5 — Statistiche senza filtri su HDT o modello

Calcola count, media, minimo e massimo della proprietà "heartRate" per tutti i
Digital Twin dal 1 luglio 2026 incluso all'8 luglio 2026 escluso.

Atteso: `POST /query/event/stats` con `hdtIds`, `modelIds` e `modelNames` vuoti,
oltre a `propertyName`, `from` e `to`.
