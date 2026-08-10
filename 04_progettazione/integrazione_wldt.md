# Integrazione dell'Agent Service nel sistema WLDT

## Obiettivo

Aggiungere al Query Workbench una modalità di interrogazione in linguaggio
naturale senza trasferire logica LLM nel frontend o nel Persistence Service.

L'Agent Service rimane un componente esterno che utilizza le API REST già
esposte dal Persistence Service.

## Architettura

```text
Utente
  │
  ▼
Query Workbench
  │
  │ POST /query
  ▼
Agent Service
Python / FastAPI
  │
  ├────────► Ollama / Qwen3 8B
  │
  └────────► Persistence Service
                    │
                    ▼
                  MongoDB
```

## Stato dell'Agent Service

Il backend dell'agente è implementato.

Espone:

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

La pipeline `POST /query` comprende:

```text
caricamento OpenAPI
→ catalogo
→ selezione top 3
→ prompt ristretto
→ generazione Ollama
→ informazioni mancanti
→ validazione OpenAPI
→ preparazione HTTP
→ esecuzione Persistence
→ risposta
```

## Contratto corrente di `POST /query`

La richiesta contiene il testo naturale:

```json
{
  "query": "Mostrami lo snapshot del Digital Twin HDT-001"
}
```

Eventuali informazioni aggiuntive provenienti dalla UI dovranno essere
introdotte tramite un'estensione esplicita del contratto qualora risultino
necessarie durante l'integrazione frontend.

## Informazioni mancanti

Quando il modello segnala informazioni necessarie non disponibili nella
richiesta, l'Agent Service restituisce HTTP 422.

Il frontend dovrà mostrare all'utente quali informazioni sono richieste e
permettere l'invio di una nuova richiesta.

## Errori

L'integrazione deve distinguere almeno:

```text
422 — informazioni necessarie mancanti
502 — output LLM o chiamata generata non utilizzabile
503 — servizio esterno necessario non raggiungibile
```

## OpenAPI

La specifica viene recuperata dinamicamente tramite:

```text
OPENAPI_SPEC_URL
```

Il documento corrente viene utilizzato per:

- catalogo;
- selezione;
- prompt;
- validazione.

## Persistence Service

L'Agent Service invia normali richieste REST verso:

```text
PERSISTENCE_SERVICE_BASE_URL
```

Non viene introdotta logica LLM nel backend Kotlin.

## Integrazione frontend prevista

La modifica al Query Workbench deve essere additiva.

L'obiettivo è introdurre una nuova modalità dedicata al linguaggio naturale
senza riscrivere le funzionalità già esistenti.

La UI dovrà almeno gestire:

- campo della richiesta;
- invio;
- stato di caricamento;
- risposta;
- informazioni mancanti;
- errori dell'Agent Service.

## Verifica già eseguita

La pipeline completa è stata testata contro un Persistence Service simulato.

Il mock ha permesso di verificare:

- caricamento OpenAPI;
- selezione;
- generazione;
- validazione;
- preparazione HTTP;
- effettiva esecuzione della richiesta.

Il benchmark finale comprende 15 esecuzioni.

I risultati sono documentati in:

```text
03_risultati/benchmark_pipeline_finale.md
```

## Dipendenza aperta

La verifica sul sistema WLDT reale richiede l'ambiente completo del progetto.

Fino a tale verifica il benchmark end-to-end utilizza il Persistence Service
simulato.

## Passi successivi

```text
ambiente WLDT completo
→ verifica contro Persistence reale
→ integrazione Query Workbench
→ test frontend → agent → persistence
```