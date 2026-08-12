# Integrazione dell'Agent Service nel sistema WLDT

## Obiettivo

Aggiungere al Query Workbench una modalità di interrogazione in linguaggio
naturale senza trasferire la logica LLM nel frontend o nel Persistence Service.
L'Agent Service rimane un componente separato che utilizza le API REST già
esposte dal Persistence Service e si adatta al relativo contratto OpenAPI.

## Architettura finale

```text
Utente
  │
  ▼
Query Workbench
  │
  ▼
Natural Language
  │
  ▼
Next.js Route Handler
  │
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

## Agent Service

L'Agent Service espone:

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

La pipeline `POST /query` comprende:

```text
caricamento OpenAPI
→ catalogo delle operazioni
→ selezione top 3
→ costruzione del prompt
→ generazione tramite Ollama
→ gestione delle informazioni mancanti
→ validazione OpenAPI
→ preparazione HTTP
→ esecuzione sul Persistence Service
→ risposta
```

## Contratto di `POST /query`

La richiesta contiene il testo naturale:

```json
{
  "query": "Mostrami lo snapshot del Digital Twin TEST-001"
}
```

Il contratto corrente non richiede un campo di contesto aggiuntivo.
Eventuali informazioni necessarie devono quindi essere presenti nella richiesta
naturale oppure essere segnalate dal modello tramite `missingInformation`.

## Informazioni mancanti

Quando il modello individua informazioni necessarie che non possono essere
ricavate dalla richiesta, l'Agent Service interrompe la pipeline e restituisce
HTTP 422.
La chiamata non raggiunge quindi il Persistence Service.

## Errori

L'integrazione distingue:

```text
422 — informazioni necessarie mancanti
502 — output LLM o chiamata generata non utilizzabile
503 — servizio esterno necessario non raggiungibile
```

Gli errori restituiti direttamente dal Persistence Service vengono mantenuti
distinti dagli errori di comunicazione con il servizio.

## Utilizzo dinamico della OpenAPI

La specifica viene recuperata attraverso:

```text
OPENAPI_SPEC_URL
```

Nello stack Docker development viene utilizzato:

```text
http://persistence-service:8081/openapi.yaml
```

La specifica corrente viene utilizzata per:

- costruire il catalogo delle operazioni;
- selezionare le candidate;
- fornire al modello un contesto ristretto;
- validare la chiamata proposta.

L'Agent Service non mantiene come sorgente operativa una lista statica
indipendente degli endpoint.

## Comunicazione con il Persistence Service

L'Agent Service invia normali richieste REST verso:

```text
PERSISTENCE_SERVICE_BASE_URL
```

Nello stack Docker development il valore utilizzato è:

```text
http://persistence-service:8081
```

Non viene introdotta logica LLM nel backend Kotlin e non sono richieste
modifiche al contratto del Persistence Service per interpretare il linguaggio
naturale.

## Containerizzazione

L'Agent Service è stato containerizzato e aggiunto al file
`docker-compose.dev.yml` dello stack WLDT.
Il build context utilizzato è:

```text
../../Tesi-WLDT/05_codice/agent_service
```

All'interno della rete Compose il Persistence Service viene raggiunto tramite
il relativo nome di servizio.
Ollama rimane invece in esecuzione sull'host Windows e viene raggiunto dal
container tramite:

```text
http://host.docker.internal:11434
```

## Integrazione nel Query Workbench

Il Query Workbench è stato esteso introducendo una nuova modalità:

```text
Natural Language
```

La modifica è additiva e non sostituisce le modalità di interrogazione già
presenti.
Il pannello dedicato permette di:

- inserire una richiesta naturale;
- avviare l'elaborazione;
- visualizzare lo stato di caricamento;
- mostrare eventuali errori;
- visualizzare la chiamata REST generata;
- visualizzare l'esito della validazione;
- mostrare la risposta del Persistence Service.

Quando possibile, i risultati vengono rappresentati in forma tabellare.

## Comunicazione frontend → Agent Service

Una prima integrazione utilizzava una rewrite Next.js:

```text
/api/agent/:path*
→
http://agent-service:8000/:path*
```

Durante una richiesta completa è stato osservato:

```text
ECONNRESET
socket hang up
```

La comunicazione diretta dal container frontend all'Agent Service è stata
verificata separatamente con successo, sia tramite `/health` sia tramite
`POST /query`. Il problema è stato quindi isolato nel meccanismo di rewrite.
La soluzione finale utilizza una Route Handler esplicita:

```text
src/app/api/agent/query/route.ts
```

Il browser invia:

```text
POST /api/agent/query
```

e la Route Handler inoltra server-side la richiesta a:

```text
http://agent-service:8000/query
```

utilizzando:

```text
AGENT_SERVICE_URL
```

Il browser non deve quindi conoscere direttamente l'indirizzo interno del
servizio nella rete Docker.

## Verifica con il Persistence Service reale

L'Agent Service è stato verificato contro il Persistence Service reale
utilizzando il Digital Twin:

```text
TEST-001
```

La richiesta naturale:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

ha prodotto:

```text
GET /hdts/{id}/snapshot
id = TEST-001
```

La chiamata ha superato la validazione e il Persistence Service ha restituito
HTTP 200 con i valori effettivamente memorizzati.

## Verifica end-to-end dal browser

Dopo l'integrazione frontend è stato verificato il flusso completo:

```text
Browser
→ Query Workbench
→ Natural Language
→ Next.js Route Handler
→ Agent Service
→ OpenAPI corrente
→ selezione delle candidate
→ Qwen3 8B
→ validazione
→ Persistence Service
→ MongoDB
→ risultato nel browser
```

Il risultato è stato visualizzato correttamente nel Query Workbench.
Questa verifica costituisce uno smoke test di integrazione sul sistema WLDT
reale e rimane distinta dal benchmark quantitativo controllato della pipeline.

## Stato

Al checkpoint del 12/08/2026 l'integrazione funzionale prevista è completata.
Rimangono separate le successive attività di:

- valutazione su richieste indipendenti dai casi utilizzati durante lo sviluppo;
- eventuali modifiche richieste durante la revisione;
- rifinitura e stesura definitiva della tesi.