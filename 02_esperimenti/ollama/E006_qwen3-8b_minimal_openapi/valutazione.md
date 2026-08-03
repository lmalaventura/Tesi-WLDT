# Valutazione E006

## Esperimento

**Nome:** E006 – Traduzione NL → API tramite Qwen3 8B con OpenAPI minimale  
**Data:** 29/07/2026  
**Modello:** Qwen3 8B  
**Esecuzione:** locale tramite Ollama 0.12.5

## Obiettivo

Verificare se la riduzione del contratto OpenAPI ai soli endpoint necessari
al benchmark migliori la capacità di Qwen3 8B di individuare e utilizzare
correttamente le operazioni disponibili.

Rispetto a E004 sono rimasti invariati:

- modello;
- prompt;
- cinque richieste del benchmark;
- metodo di esecuzione;
- criteri di valutazione.

È stata modificata esclusivamente la quantità di informazioni presenti
nell'OpenAPI.

## OpenAPI utilizzata

La versione minimale conteneva esclusivamente:

- GET /hdts
- GET /hdts/{id}/snapshot
- POST /query/event/values/history
- POST /query/event/stats
- POST /query/event/comparison

Sono stati mantenuti anche tutti gli schemi referenziati necessari alla
comprensione delle richieste e dei body.

## Osservazioni

La riduzione dell'OpenAPI non ha prodotto un miglioramento evidente.

Il modello continua a:

- dichiarare assenti endpoint realmente presenti nel documento;
- inventare endpoint semanticamente plausibili;
- riconoscere alcuni concetti presenti negli schemi senza associarli ai
  relativi path;
- costruire parametri non previsti dal contratto;
- usare gli schemi come indizi semantici invece di attenersi rigorosamente
  alla sezione paths.

Gli endpoint inventati includono:

- GET /digital-twins
- GET /hdt/{hdtId}/properties
- GET /hdt/{hdtId}/property/{propertyName}/history
- GET /hdt/properties/filter
- POST /stats

Per Q5 il modello ha riconosciuto correttamente lo scopo dello schema
PropertyStatsRequest e la presenza dei campi obbligatori, ma ha inventato
valori non forniti dalla richiesta e non ha utilizzato il path reale
/query/event/stats.

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

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 2/2
- Totale: 5/10

## Punteggio complessivo

**14/50**

## Confronto con E004

E004 utilizzava lo stesso modello e l'OpenAPI completa.

E006 utilizza lo stesso modello e una versione ridotta ai soli endpoint
necessari.

Il comportamento è rimasto sostanzialmente invariato. Non emergono evidenze
che la dimensione complessiva dell'OpenAPI sia la causa principale degli
errori osservati.

## Esito

**INSUFFICIENTE**

L'ipotesi secondo cui il modello fallisse principalmente a causa della
quantità di informazioni irrilevanti presenti nell'OpenAPI non è supportata
da questo esperimento.

Qwen3 8B continua a non effettuare un grounding affidabile sui path, anche
quando il documento contiene esclusivamente gli endpoint necessari.