# Valutazione E005

## Esperimento

**Nome:** E005 – Traduzione NL → API tramite Llama 3.1 8B  
**Data:** 29/07/2026  
**Modello:** Llama 3.1 8B  
**Esecuzione:** locale tramite Ollama

## Obiettivo

Valutare se il cambiamento della famiglia del modello, mantenendo invariati
OpenAPI, prompt e benchmark, migliori la capacità di tradurre richieste in
linguaggio naturale nelle chiamate API WLDT corrette.

## Osservazioni

Il modello ha generato rapidamente una risposta chiara e ben strutturata,
ma non ha utilizzato fedelmente gli endpoint presenti nell'OpenAPI.

Ha invece costruito un'API REST semanticamente plausibile basata sul
concetto di Digital Twin, introducendo endpoint inesistenti:

- GET /digital-twins
- GET /digital-twins/{hdtId}/properties
- GET /digital-twins/{hdtId}/properties/{propertyName}/history
- POST /digital-twins/search
- POST /digital-twins/statistics

Per Q4 il modello ha riconosciuto correttamente la struttura logica del
confronto, utilizzando propertyName, operatore GT e valore 150. Tuttavia,
l'endpoint proposto non è presente nel contratto OpenAPI.

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
- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 2/2
- Fedeltà OpenAPI: 1/2
- Gestione informazioni mancanti: 0/2
- Totale: 5/10

### Q5
- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 0/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 2/10

## Punteggio complessivo

15/50

## Esito

INSUFFICIENTE.

Il cambiamento dalla famiglia Qwen3 a Llama 3.1 non ha risolto il problema
di grounding sul contratto OpenAPI.

Llama 3.1 8B è risultato più rapido nell'esecuzione e non ha mostrato
reasoning esplicito, ma ha prodotto endpoint inventati sulla base di una
struttura API semanticamente plausibile.