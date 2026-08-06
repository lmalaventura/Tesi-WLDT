# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste espresse in linguaggio
naturale in chiamate REST verso il Persistence Service WLDT.

## Stato attuale

L'Agent Service:

- recupera dinamicamente la specifica OpenAPI;
- costruisce un catalogo normalizzato delle operazioni;
- seleziona le operazioni candidate rispetto alla richiesta dell'utente;
- costruisce un prompt limitato ai candidati e agli schemi referenziati;
- interroga un modello locale tramite Ollama;
- richiede un output conforme a un JSON Schema generale;
- valida metodo, endpoint, parametri e request body rispetto all'OpenAPI;
- blocca le chiamate semanticamente non conformi;
- prepara l'URL finale, i query parameter e il body della richiesta HTTP.

L'esecuzione effettiva verso il Persistence Service e la gestione della
relativa risposta non sono ancora collegate.

## Avvio

```powershell
uv run uvicorn app.main:app --reload