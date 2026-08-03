# Architettura WLDT rilevante per la tesi

## Componenti esistenti

- **WHDT Monitor Frontend**: applicazione Next.js/TypeScript che contiene il
  Query Workbench e comunica con i servizi WLDT.
- **Persistence Service**: backend Kotlin/Ktor che espone le API per HDT,
  modelli, proprietà, osservazioni, viste e query.
- **MongoDB**: sistema di persistenza utilizzato dal Persistence Service.
- **Contratto API**: specifica OpenAPI v0.2.0 pubblicata dal Persistence
  Service anche tramite `GET /openapi.yaml`.

## Flusso attuale

```text
Utente
  → Query Workbench
  → costruzione guidata della richiesta
  → Persistence Service
  → MongoDB
  → risultato mostrato nel frontend
```

## Estensione prevista dalla tesi

```text
Utente
  → nuova scheda del Query Workbench
  → richiesta in linguaggio naturale
  → Agent Service Python
      → acquisizione della OpenAPI aggiornata
      → selezione delle operazioni candidate
      → costruzione del prompt
      → modello locale tramite Ollama
      → validazione della chiamata
      → esecuzione sul Persistence Service
  → inoltro del risultato al frontend
```

L'Agent Service deve adattarsi al contratto e al comportamento del sistema
esistente. Nella prima integrazione non è prevista una modifica della logica
del Persistence Service. L'intervento sul frontend è limitato all'aggiunta
della nuova scheda e del client necessario a chiamare l'Agent Service.
