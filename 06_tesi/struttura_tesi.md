# Struttura provvisoria della tesi

## Titolo provvisorio

Traduzione di richieste in linguaggio naturale in chiamate REST per il
sistema WLDT

Il titolo deve essere confermato con la relatrice.

## Capitolo 1 — Introduzione

- contesto generale;
- problema affrontato;
- obiettivo del lavoro;
- contributi principali;
- organizzazione della tesi.

## Capitolo 2 — Contesto tecnologico

- sistema WLDT;
- Persistence Service;
- contratto OpenAPI;
- Large Language Model;
- modelli locali e Ollama.

## Capitolo 3 — Analisi del problema

- requisiti funzionali;
- requisiti non funzionali;
- vincoli del sistema esistente;
- formato della chiamata generata;
- rischi di allucinazione degli endpoint.

## Capitolo 4 — Metodologia sperimentale

- definizione del benchmark;
- richieste utilizzate;
- modelli confrontati;
- criteri di valutazione;
- risultati preliminari.

## Capitolo 5 — Progettazione della pipeline

- architettura dell'Agent Service;
- caricamento dinamico dell'OpenAPI;
- catalogo delle operazioni;
- selezione delle API candidate;
- costruzione del prompt;
- validazione;
- esecuzione della chiamata REST.

## Capitolo 6 — Implementazione

- FastAPI;
- organizzazione del codice;
- integrazione con Ollama;
- gestione della configurazione;
- testing.

## Capitolo 7 — Integrazione e valutazione

- collegamento con il Persistence Service;
- collegamento con il Query Workbench;
- test end-to-end;
- benchmark finale;
- limiti della soluzione.

## Capitolo 8 — Conclusioni

- risultati ottenuti;
- risposta agli obiettivi;
- sviluppi futuri.