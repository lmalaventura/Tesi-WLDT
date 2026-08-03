# Valutazione E003

## Esperimento

- **Nome:** E003 — Traduzione NL → API tramite Qwen3 4B
- **Data:** 28/07/2026
- **Esecuzione:** locale tramite Ollama

## Osservazioni

Il modello non utilizza gli endpoint presenti nella sezione `paths`. Nella
risposta finale dichiara impossibile Q1, usa un endpoint inesistente `/execute`
per Q2–Q5 e costruisce viste e campi non definiti dal contratto. Inoltre altera
il contenuto di Q4 e Q5, sostituendo proprietà, soglie e obiettivo della
richiesta.

## Valutazione per richiesta

### Q1

- Metodo HTTP: 0/2
- Endpoint: 0/2
- Input: 2/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 2/10

### Q2

- Metodo HTTP: 0/2
- Endpoint: 0/2
- Input: 0/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 0/10

### Q3

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 3/10

### Q4

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 0/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 2/10

### Q5

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 0/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 2/10

## Punteggio complessivo

**9/50**

## Esito

**INSUFFICIENTE**

Il risultato non è utilizzabile per generare richieste REST senza una fase di
selezione e validazione esterna al modello.
