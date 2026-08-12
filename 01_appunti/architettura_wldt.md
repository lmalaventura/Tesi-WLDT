# Architettura WLDT rilevante per la tesi

## Componenti esistenti

- **WHDT Monitor Frontend**: applicazione Next.js/TypeScript che contiene il
  Query Workbench e comunica con i servizi WLDT.
- **HDT Creation Service**: servizio utilizzato per i flussi di creazione e
  importazione dei Digital Twin.
- **Persistence Service**: backend Kotlin/Ktor che espone le API per HDT,
  modelli, proprietà, osservazioni, viste e query.
- **MongoDB**: sistema di persistenza utilizzato dal Persistence Service.
- **Contratto API**: specifica OpenAPI pubblicata dal Persistence Service anche
  tramite `GET /openapi.yaml`.

## Flusso WLDT di partenza

Prima dell'estensione sviluppata nella tesi, il Query Workbench permetteva di
costruire le interrogazioni tramite le modalità già previste dal frontend.
In forma semplificata:

```text
Utente
  ↓
Query Workbench
  ↓
costruzione guidata della richiesta
  ↓
Persistence Service
  ↓
MongoDB
  ↓
risultato mostrato nel frontend
```

## Estensione implementata nella tesi

La soluzione aggiunge un Agent Service Python e una modalità Natural Language
nel Query Workbench.
Il flusso finale è:

```text
Utente
  ↓
Query Workbench
  ↓
Natural Language
  ↓
Next.js Route Handler
  ↓
Agent Service
  ↓
  ├── recupero OpenAPI corrente
  ├── selezione delle operazioni candidate
  ├── costruzione del prompt
  ├── Qwen3 8B tramite Ollama
  ├── validazione della chiamata
  └── preparazione ed esecuzione REST
  ↓
Persistence Service
  ↓
MongoDB
  ↓
risultato restituito al frontend
```

## Separazione delle responsabilità

L'Agent Service si adatta al contratto e al comportamento del Persistence
Service esistente.
La logica LLM non viene introdotta nel backend Kotlin e il Persistence Service
non viene modificato per interpretare il linguaggio naturale.
Le responsabilità rimangono quindi separate:

```text
Frontend
→ acquisizione della richiesta e presentazione del risultato

Agent Service
→ interpretazione NL-to-REST e controllo della chiamata

Persistence Service
→ esecuzione delle API e accesso ai dati

MongoDB
→ persistenza
```

## OpenAPI dinamica

L'Agent Service recupera la specifica OpenAPI direttamente dal Persistence
Service in esecuzione.
Nello stack Docker development viene utilizzato:

```text
http://persistence-service:8081/openapi.yaml
```

La specifica viene quindi utilizzata come fonte per:

- costruzione del catalogo;
- selezione delle candidate;
- costruzione del contesto del modello;
- validazione della chiamata prodotta.

L'agente non mantiene come sorgente operativa una lista statica indipendente
degli endpoint.

## Comunicazione con Ollama

Qwen3 8B viene eseguito tramite Ollama sull'host Windows.
L'Agent Service containerizzato lo raggiunge tramite:

```text
http://host.docker.internal:11434
```

Il runtime LLM rimane quindi esterno allo stack Compose, mentre l'Agent Service
e i servizi WLDT sono containerizzati.

## Comunicazione frontend → Agent Service

La prima integrazione aveva utilizzato una rewrite Next.js dedicata
all'Agent Service.
Durante le richieste complete è stato osservato un errore di proxy
`ECONNRESET / socket hang up`.
La comunicazione diretta tra il container frontend e l'Agent Service è stata
verificata separatamente con successo, permettendo di isolare il problema nel
meccanismo di rewrite.
La soluzione finale utilizza una Route Handler Next.js:

```text
src/app/api/agent/query/route.ts
```

Il browser chiama:

```text
POST /api/agent/query
```

e la Route Handler inoltra la richiesta server-side a:

```text
http://agent-service:8000/query
```

tramite la variabile runtime:

```text
AGENT_SERVICE_URL
```

## Verifica finale

Il 12/08/2026 è stato verificato il flusso end-to-end utilizzando il Digital
Twin di test:

```text
TEST-001
```

Una richiesta naturale relativa alle proprietà correnti ha prodotto:

```text
GET /hdts/{id}/snapshot
```

La chiamata è risultata valida rispetto alla OpenAPI, è stata eseguita sul
Persistence Service e la risposta HTTP 200 è stata visualizzata nel Query
Workbench.
Questo test verifica l'integrazione funzionale:

```text
browser
→ frontend
→ Agent Service
→ Ollama
→ Persistence Service
→ MongoDB
→ frontend
```