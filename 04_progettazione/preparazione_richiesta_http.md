# Preparazione della richiesta HTTP

## Obiettivo

Trasformare una chiamata REST già validata in una richiesta HTTP concreta,
pronta per essere inviata al Persistence Service.

La preparazione viene eseguita soltanto dopo il superamento della
validazione OpenAPI. Il componente non decide quale operazione utilizzare e
non corregge l'output del modello.

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

## Esecuzione della richiesta

La struttura `PreparedApiRequest` viene utilizzata dal `RestClient` come
unico input per l'esecuzione HTTP.

Il client utilizza metodo, URL, query parameter ed eventuale body già
preparati dai componenti precedenti. Non seleziona endpoint e non modifica
la chiamata ricevuta.

Le risposte HTTP del Persistence Service vengono mantenute distinguendo:

- status code;
- content type;
- contenuto della risposta.

Uno status code di errore restituito dal Persistence Service non viene
considerato automaticamente un errore di comunicazione. Per esempio, una
risposta `404` indica che il servizio è stato raggiunto e ha risposto alla
richiesta.

Gli errori di trasporto, come l'impossibilità di stabilire la connessione,
vengono invece trattati separatamente e provocano una risposta `503`
dell'Agent Service.