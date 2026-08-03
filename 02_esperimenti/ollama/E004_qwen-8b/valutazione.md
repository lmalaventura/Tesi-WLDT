# Valutazione E004

## Esperimento

- **Nome:** E004 — Traduzione NL → API tramite Qwen3 8B
- **Data:** 29/07/2026
- **Esecuzione:** locale tramite Ollama

## Osservazioni

Il modello riconosce il metodo GET per Q1 e Q2 e alcuni concetti degli schemi,
ma non recupera i path reali. Propone `/views`, `/views/{hdtId}` e
`/events/comparison` come endpoint ipotetici e dichiara assenti operazioni che
sono presenti nel contratto.

## Valutazione per richiesta

### Q1

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 2/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 4/10

### Q2

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 3/10

### Q3

- Metodo HTTP: 0/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 1/10

### Q4

- Metodo HTTP: 0/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 1/10

### Q5

- Metodo HTTP: 0/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 1/10

## Punteggio complessivo

**10/50**

## Esito

**INSUFFICIENTE**

Rispetto a Qwen3 4B non emerge un miglioramento rilevante nel grounding sulla
specifica completa.
