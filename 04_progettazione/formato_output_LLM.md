# Formato dell'output prodotto dall'LLM

## Obiettivo

Il modello non restituisce una descrizione testuale della chiamata da eseguire.

La comunicazione tra LLM e codice applicativo utilizza un oggetto JSON
strutturato rappresentato da `GeneratedApiCall`.

## Struttura generale

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

## `method`

Metodo HTTP dell'operazione selezionata.

Lo schema di output viene ristretto ai metodi presenti tra le operazioni
candidate.

## `endpoint`

Path OpenAPI dell'operazione.

Deve essere mantenuto nella forma dichiarata dalla specifica.

Per esempio:

```text
/hdts/{id}/snapshot
```

Il valore concreto di `{id}` non viene inserito direttamente nel path prodotto
dal modello.

## `pathParameters`

Contiene i valori dei placeholder presenti nel path.

Esempio:

```json
{
  "id": "HDT-001"
}
```

## `queryParameters`

Contiene i parametri destinati alla query string.

Quando non sono necessari viene utilizzato un oggetto vuoto.

## `body`

Contiene il request body.

Può essere:

- `null`;
- un oggetto;
- un array;
- un altro tipo JSON previsto dall'OpenAPI.

La struttura radice deve coincidere con lo schema dell'operazione.

Per esempio `valuesByName` utilizza un array:

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

## `missingInformation`

Contiene le informazioni necessarie alla costruzione della richiesta ma non
determinabili senza inventare dati.

Se la lista non è vuota, la pipeline non esegue la chiamata.

## JSON Schema dinamico

Il modello Pydantic definisce il formato generale di `GeneratedApiCall`.

Prima della generazione, `PromptBuilder` costruisce però uno schema più
ristretto sulla base delle candidate.

Possono essere limitati:

- `method`;
- `endpoint`;
- tipo radice del body;
- campi obbligatori;
- alcuni requisiti specifici delle operazioni.

## Riferimenti OpenAPI

Il prompt contiene gli schemi OpenAPI rilevanti per interpretare le candidate.

Il JSON Schema autonomo passato a Ollama non mantiene invece riferimenti
`$ref` OpenAPI non risolvibili nel documento di structured output.

Quando necessario, tali riferimenti vengono ridotti a vincoli strutturali.

La verifica completa dello schema rimane responsabilità
dell'`ApiCallValidator`.

## Regole semantiche del prompt

Il prompt specifica inoltre alcune convenzioni, tra cui:

- usare `propertyName` quando viene indicato il nome della proprietà;
- usare `propertyId` soltanto quando viene fornito esplicitamente un
  identificatore;
- mantenere gli array obbligatori di `/query/event/stats`;
- utilizzare array vuoti per tali filtri quando la dimensione non viene
  ristretta;
- non inventare endpoint, parametri o valori necessari.

## Separazione tra formato e validazione

Un output formalmente compatibile con `GeneratedApiCall` non è automaticamente
una chiamata valida rispetto alla OpenAPI.

L'oggetto viene sempre sottoposto al validatore deterministico prima
dell'esecuzione.