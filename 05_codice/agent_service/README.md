# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste espresse in linguaggio
naturale in chiamate REST verso il Persistence Service WLDT.

## Stato attuale

L'Agent Service:

- recupera dinamicamente la specifica OpenAPI dal Persistence Service;
- costruisce un catalogo normalizzato delle operazioni REST;
- analizza la richiesta in linguaggio naturale;
- restituisce un elenco ordinato di operazioni candidate.

La selezione utilizza path, operationId, descrizioni, tag e parametri
dell'OpenAPI. Il modello LLM, la validazione finale e l'esecuzione della
chiamata REST non sono ancora collegati.

Quando il Persistence Service non è raggiungibile, gli endpoint che dipendono
dalla specifica OpenAPI restituiscono `503 Service Unavailable`.


## Avvio

```powershell
uv run uvicorn app.main:app --reload