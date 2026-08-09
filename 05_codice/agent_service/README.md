# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste espresse in linguaggio
naturale in chiamate REST verso il Persistence Service WLDT.

## Stato attuale

L'Agent Service:

- recupera dinamicamente la specifica OpenAPI;
- costruisce un catalogo normalizzato delle operazioni;
- seleziona le operazioni candidate rispetto alla richiesta dell'utente;
- costruisce un prompt ristretto;
- interroga Qwen3 tramite Ollama;
- riceve un output JSON strutturato;
- valida la chiamata rispetto alla specifica OpenAPI;
- prepara la richiesta HTTP concreta;
- esegue la richiesta mediante un `RestClient`;
- restituisce al client status code e contenuto della risposta del
  Persistence Service.

L'esecuzione reale nell'ambiente WLDT completo deve ancora essere verificata
quando sarà disponibile l'infrastruttura necessaria.
## Avvio

```powershell
uv run uvicorn app.main:app --reload