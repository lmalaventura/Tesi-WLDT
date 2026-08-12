# Preparazione della richiesta HTTP

## Obiettivo

Trasformare una chiamata REST già validata in una richiesta HTTP concreta,
pronta per essere inviata al Persistence Service.
La preparazione viene eseguita soltanto dopo il superamento della validazione
OpenAPI. Il componente non decide quale operazione utilizzare e non corregge
l'output del modello.

## Input

L'`ApiRequestPreparer` riceve:

- una struttura `GeneratedApiCall`;
- il base URL del Persistence Service.

La chiamata contiene:

- metodo HTTP;
- path OpenAPI;
- path parameter;
- query parameter;
- eventuale request body.

## Costruzione dell'URL

Il path generato dal modello conserva inizialmente i placeholder definiti
nell'OpenAPI, per esempio:

```text
/hdts/{id}/snapshot
```

Il valore concreto viene invece mantenuto separatamente:

```json
{
  "id": "TEST-001"
}
```

Durante la preparazione, il placeholder viene sostituito con il relativo valore
e il path ottenuto viene combinato con il base URL configurato.
Nel caso dello stack Docker development:

```text
base URL
http://persistence-service:8081

path OpenAPI
/hdts/{id}/snapshot

path parameter
id = TEST-001

URL preparato
http://persistence-service:8081/hdts/TEST-001/snapshot
```

I valori vengono codificati prima di essere inseriti nel percorso.

## Query parameter

Gli eventuali query parameter vengono mantenuti separati dall'URL durante la
preparazione e passati successivamente al client HTTP.
Questo evita di costruire manualmente la query string e permette al client di
gestire correttamente la codifica dei valori.

## Request body

Se l'operazione prevede un request body, il contenuto già validato viene
mantenuto nella richiesta preparata. `ApiRequestPreparer` non modifica semanticamente il body e non prova a
correggere valori prodotti dal modello.

## `PreparedApiRequest`

Il risultato della preparazione è una struttura `PreparedApiRequest` contenente
le informazioni necessarie all'esecuzione:

- metodo HTTP;
- URL completo;
- query parameter;
- eventuale body.

In questo modo la selezione e la validazione rimangono separate
dall'esecuzione HTTP.

## Esecuzione della richiesta

La struttura `PreparedApiRequest` viene utilizzata dal `RestClient` come unico
input per l'esecuzione verso il Persistence Service. Il client utilizza metodo, URL, query parameter ed eventuale body 
già preparati dai componenti precedenti. Non seleziona endpoint e non modifica la chiamata ricevuta.
Le risposte HTTP del Persistence Service vengono mantenute distinguendo:

- status code;
- content type;
- contenuto della risposta.

Uno status code di errore restituito dal Persistence Service non viene
considerato automaticamente un errore di comunicazione. Per esempio, una
risposta HTTP 404 indica che il servizio è stato raggiunto e ha risposto alla
richiesta.
Gli errori di trasporto, come l'impossibilità di stabilire la connessione,
vengono invece trattati separatamente e provocano una risposta HTTP 503
dell'Agent Service.