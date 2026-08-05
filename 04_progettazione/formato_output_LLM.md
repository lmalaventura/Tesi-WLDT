# Formato dell'output prodotto dall'LLM

## Obiettivo

Il modello deve restituire esclusivamente un oggetto JSON. Testo esplicativo,
Markdown o endpoint sostituiti con valori concreti non sono ammessi.

## Schema logico

```json
{
  "method": "POST",
  "endpoint": "/query/event/comparison",
  "pathParameters": {},
  "queryParameters": {},
  "body": {
    "comparisons": [
      {
        "propertyName": "systolicPressure",
        "comparison": "GT",
        "value": 150
      }
    ]
  },
  "missingInformation": []
}
```

## Campi

### `method`

Metodo HTTP associato all'operazione candidata.

### `endpoint`

Path template riportato nella OpenAPI, senza sostituire i placeholder. Per
esempio, deve rimanere `/hdts/{id}/snapshot`.

### `pathParameters`

Oggetto che associa ogni placeholder al valore ricavato dalla richiesta.

```json
{
  "id": "HDT-001"
}
```

### `queryParameters`

Parametri da inserire nella query string. Deve essere un oggetto vuoto quando
l'operazione non ne prevede.

### `body`

Corpo JSON della richiesta. Deve essere `null` per le operazioni che non
prevedono un body e rispettare lo schema OpenAPI negli altri casi.

### `missingInformation`

Elenco delle informazioni obbligatorie non ricavabili né dalla frase né dal
contesto fornito dal client. Il modello non deve inventare valori per riempire
i campi mancanti.

## Vincoli

- metodo ed endpoint devono corrispondere alla stessa operazione candidata;
- il path deve essere copiato esattamente dal catalogo;
- i path parameter concreti devono comparire solo in `pathParameters`;
- non sono ammessi campi estranei allo schema;
- l'output non autorizza l'esecuzione: deve essere prima validato.

## Distinzione dalla risposta dell'Agent Service

Questo documento descrive l'output interno dell'LLM. La risposta HTTP esposta
al frontend include anche stato, risultato del Persistence Service ed
informazioni sull'errore, come definito in `integrazione_wldt.md`.

## Limiti della generazione strutturata

La conformità dell’output al modello `GeneratedApiCall` garantisce soltanto
che la risposta possieda i campi generali richiesti dall’Agent Service.

Non garantisce invece che il contenuto del campo `body` rispetti lo schema
specifico dell’operazione OpenAPI selezionata.

Durante uno smoke test relativo a una richiesta storica con intervallo
temporale, il modello ha selezionato correttamente l’endpoint
`POST /query/event/values/valuesByName`, ma ha generato un oggetto JSON al
posto dell’array richiesto dal request body.

Il modello ha inoltre utilizzato il campo `propertyId` per un valore che
rappresentava il nome della proprietà e che avrebbe quindi dovuto essere
inserito in `propertyName`.

Questo risultato mostra che l’uso di un JSON Schema generale per l’output non
rende superflua la validazione semantica rispetto alla specifica OpenAPI della
singola operazione.
