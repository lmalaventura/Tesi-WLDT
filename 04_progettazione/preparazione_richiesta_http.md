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