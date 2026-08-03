# Integrazione dell'Agent Service nel sistema WLDT

## Obiettivo

Aggiungere al Query Workbench una modalità di interrogazione in linguaggio
naturale senza trasferire logica LLM nel frontend o nel Persistence Service.
L'Agent Service deve adattarsi ai contratti e ai componenti WLDT esistenti.

## Sistema attuale analizzato

Il frontend `whdt-monitor-frontend` è un'applicazione Next.js. Il Query
Workbench è implementato in:

```text
src/app/query-builder/QueryWorkbench.tsx
src/app/query-builder/panels/
```

Nella versione analizzata espone tre schede: Observation, Property e Views.
Il frontend utilizza tipi generati dalla OpenAPI e contiene già un rewrite per
inoltrare `/api/persistence/*` al Persistence Service.

Il `persistence-service` è un'applicazione Kotlin/Ktor collegata a MongoDB. La
specifica effettivamente servita dal backend è disponibile tramite:

```text
GET /openapi.yaml
```

Non sono previste modifiche alla logica del Persistence Service per la prima
integrazione.

## Architettura proposta

```text
Utente
  │
  ▼
Query Workbench — scheda Natural Language
  │ POST /api/agent/query
  ▼
Agent Service Python
  ├─ recupero/cache della OpenAPI
  ├─ selezione operazioni candidate
  ├─ generazione JSON tramite Ollama
  ├─ validazione sulla OpenAPI
  └─ esecuzione REST
       │
       ├──────────► Ollama
       └──────────► Persistence Service ──► MongoDB
  │
  ▼
Risultato o richiesta di informazioni mancanti
```

## Contratto dell'Agent Service

### `GET /health`

Verifica che il processo sia attivo. La risposta potrà includere lo stato
dell'ultima OpenAPI caricata e, in una fase successiva, la raggiungibilità di
Ollama e Persistence Service.

### `POST /query`

Esempio di richiesta:

```json
{
  "query": "Mostrami la media di heartRate per i Digital Twin selezionati",
  "context": {
    "selectedHdtIds": ["HDT-001", "HDT-002"]
  }
}
```

Il campo `context` è facoltativo e permette al frontend di fornire dati non
espressi nella frase, per esempio gli identificativi selezionati nella UI.

Esempio di successo:

```json
{
  "status": "success",
  "generatedCall": {
    "method": "POST",
    "endpoint": "/query/event/stats",
    "pathParameters": {},
    "queryParameters": {},
    "body": {
      "hdtIds": ["HDT-001", "HDT-002"],
      "modelIds": [],
      "modelNames": [],
      "propertyName": "heartRate"
    }
  },
  "missingInformation": [],
  "result": {}
}
```

Esempio di informazioni mancanti:

```json
{
  "status": "missing_information",
  "generatedCall": null,
  "missingInformation": ["id del Digital Twin"],
  "result": null,
  "error": null
}
```

Altri stati previsti:

- `validation_error`;
- `model_error`;
- `persistence_error`;
- `configuration_error`.

## Allineamento con la OpenAPI

L'Agent Service non deve dipendere da una copia aggiornata manualmente. La
specifica viene recuperata dal Persistence Service e usata per:

- costruire il catalogo delle operazioni;
- ricavare parametri e body obbligatori;
- generare il contesto compatto per il modello;
- validare la chiamata prima dell'esecuzione.

La prima implementazione deve prevedere:

1. caricamento all'avvio;
2. hash o identificatore della specifica caricata;
3. refresh configurabile;
4. ultimo documento valido mantenuto in cache;
5. errore esplicito quando nessuna specifica valida è disponibile.

La strategia di refresh definitiva verrà verificata durante l'integrazione con
l'ambiente Docker.

## Modifiche previste al frontend

Le modifiche devono essere additive e limitate al punto di integrazione:

```text
src/app/query-builder/QueryWorkbench.tsx
src/app/query-builder/panels/NaturalLanguageQueryPanel.tsx   (nuovo)
src/app/query-builder/types/agent.ts                         (nuovo, se utile)
next.config.ts                                               (rewrite Agent Service)
```

La nuova scheda deve contenere almeno:

- casella di testo per la richiesta;
- comando di invio;
- indicatore di elaborazione;
- tabella per il risultato;
- messaggio per informazioni mancanti o errori.

I componenti esistenti del Query Workbench non devono essere riscritti. La
tabella già disponibile nel frontend va riutilizzata dopo averne verificato il
contratto nell'ultima versione della repository.

## Persistence Service

L'Agent Service esegue normali richieste HTTP sugli endpoint esistenti. Non è
prevista l'aggiunta di logica LLM al backend Kotlin.

La verifica del codice ha evidenziato due aspetti da rispettare:

- `/query/event/values/history` non applica `from` e `to`; per un intervallo si
  usa `/query/event/values/valuesByName`;
- `/query/event/stats` richiede nel body gli array `hdtIds`, `modelIds` e
  `modelNames`, ma gli array vuoti rappresentano l'assenza del relativo filtro.

Queste regole riguardano l'implementazione dell'Agent Service e non richiedono
modifiche al backend.

## Configurazione iniziale

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
PERSISTENCE_SERVICE_BASE_URL=http://localhost:8081
OPENAPI_URL=http://localhost:8081/openapi.yaml
OPENAPI_REFRESH_SECONDS=300
REQUEST_TIMEOUT_SECONDS=30
```

I valori effettivi verranno adattati all'ambiente Docker. Nessuna credenziale
deve essere salvata nella repository.

## Piano di integrazione

1. creare il servizio HTTP e i modelli request/response;
2. implementare `OpenApiProvider` e catalogo dinamico;
3. portare e correggere i componenti del prototipo;
4. aggiungere validazione ed esecuzione HTTP;
5. testare con Ollama e Persistence Service simulato;
6. avviare l'ambiente Docker completo;
7. aggiungere la scheda al Query Workbench;
8. eseguire test end-to-end.

## Dipendenza ancora aperta

Al 3 agosto 2026 è stato confermato che esiste una repository Docker per
eseguire il sistema completo in locale. Il relativo collegamento deve ancora
essere ricevuto e aggiunto a `00_materiali/lista_repository.md`.
