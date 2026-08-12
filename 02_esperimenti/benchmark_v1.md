# Benchmark v1 — richieste NL per WLDT

Il benchmark è stato utilizzato per gli esperimenti E002–E006 ed E009. Gli
input originali vengono mantenuti invariati per preservare la riproducibilità
delle esecuzioni già svolte.

## Q1 — Elenco Digital Twin

Mostrami tutti i Digital Twin disponibili.

## Q2 — Valore corrente

Mostrami il valore corrente delle proprietà del Digital Twin con id "HDT-001".

## Q3 — Storico proprietà

Mostrami lo storico della proprietà "heartRate" del Digital Twin "HDT-001" tra
il 1 luglio 2026 e il 7 luglio 2026.

## Q4 — Confronto

Trova i Digital Twin per cui la proprietà "systolicPressure" ha un valore
maggiore di 150.

## Q5 — Statistiche

Calcola le statistiche della proprietà "heartRate" per i Digital Twin
selezionati nell'intervallo dal 1 luglio 2026 al 7 luglio 2026.

## Nota successiva all'analisi del backend

Il benchmark era costruito per essere risolto esclusivamente tramite OpenAPI.
Il codice del Persistence Service mostra però che Q3, quando contiene un
intervallo, deve usare `/query/event/values/valuesByName`; l'endpoint
`/query/event/values/history` ignora `from` e `to`.
Q5 dipende inoltre dal significato di “Digital Twin selezionati”. Gli array
`hdtIds`, `modelIds` e `modelNames` sono obbligatori nel body, ma
l'implementazione accetta array vuoti come assenza del relativo filtro. Se la
selezione è esterna alla frase, deve essere fornita dal client insieme alla
richiesta naturale.
