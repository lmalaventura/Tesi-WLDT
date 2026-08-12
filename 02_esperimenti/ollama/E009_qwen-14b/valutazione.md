# Valutazione E009

## Esperimento

**Nome:** E009 – Traduzione NL → API tramite Qwen3 14B  
**Data:** 31/07/2026  
**Modello:** Qwen3 14B  
**Esecuzione:** locale tramite Ollama  
**Tempo totale:** circa 12 minuti

## Obiettivo

Completare il confronto tra modelli locali di dimensioni differenti,
verificando se un modello da 14 miliardi di parametri migliori la capacità
di tradurre richieste in linguaggio naturale nelle chiamate API definite
dal contratto OpenAPI WLDT.

## Osservazioni

Il modello non individua correttamente gli endpoint principali presenti
nell'OpenAPI.
In particolare:

- dichiara inesistente `GET /hdts`;
- non riconosce `GET /hdts/{id}/snapshot`;
- non riconosce `POST /query/event/values/history`;
- inventa l'endpoint `/api/v1/comparisons`;
- utilizza schemi presenti nell'OpenAPI senza collegarli ai path corretti;
- introduce valori fittizi non presenti nella richiesta;
- non rispetta il vincolo di non inventare endpoint e strutture.

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
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 1/10

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
- Input: 1/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 3/10

### Q5

- Metodo HTTP: 2/2
- Endpoint: 0/2
- Input: 0/2
- Fedeltà OpenAPI: 0/2
- Gestione informazioni mancanti: 0/2
- Totale: 2/10

## Punteggio complessivo

**9/50**

## Prestazioni operative

Il modello è tecnicamente eseguibile sull'hardware disponibile, ma presenta:

- consumo di memoria prossimo al limite della macchina;
- circa 14 GB di RAM osservati durante l’esecuzione;
- utilizzo della GPU osservato come molto basso;
- utilizzo della CPU non misurato sistematicamente;
- tempo di circa 12 minuti per il benchmark completo.

Questi tempi non risultano adeguati per un'applicazione interattiva.

## Confronto preliminare

L'aumento della dimensione da 8B a 14B non ha migliorato il grounding
sull'OpenAPI completa.
Il modello 14B è risultato sensibilmente più lento e più oneroso in termini
di memoria, senza compensare tali costi con una maggiore correttezza.

## Esito

**INSUFFICIENTE**

Qwen3 14B non è adatto come modello principale del prototipo nelle condizioni
hardware disponibili.
Il risultato conferma che il problema osservato non viene risolto aumentando
soltanto il numero di parametri del modello.