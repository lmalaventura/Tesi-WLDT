# WLDT LLM Agent Service

Microservizio Python incaricato di tradurre richieste espresse in linguaggio
naturale in chiamate REST verso il Persistence Service WLDT.

## Stato attuale

Lo scheletro HTTP espone:

- `GET /health`;
- `POST /query`.

L'endpoint `/query` riceve e valida la richiesta, ma non utilizza ancora il
modello LLM e non esegue chiamate verso il Persistence Service.

## Avvio

```powershell
uv run uvicorn app.main:app --reload