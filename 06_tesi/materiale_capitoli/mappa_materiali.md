# Mappa dei materiali per la tesi

Documento interno di raccordo tra il lavoro tecnico svolto e la futura stesura dei capitoli.

Non costituisce testo definitivo da consegnare.

## Questione preliminare sul titolo

Il titolo originariamente ipotizzato faceva riferimento alla trasformazione NL → SQL.

Il lavoro effettivamente progettato e implementato riguarda invece:

NL → chiamata REST

guidata dalla specifica OpenAPI corrente del Persistence Service.

Titolo provvisorio attuale:

**Progettazione e implementazione di un agente LLM per la traduzione di richieste in linguaggio naturale in chiamate REST nel sistema WLDT**

Il titolo deve essere confermato con relatrice e coordinatore prima della stesura formale.

## Capitolo 1 — Introduzione

Materiali principali:

- `06_tesi/bozze/01_introduzione_obiettivi.md`;
- `01_appunti/architettura_wldt.md`;
- `04_progettazione/integrazione_wldt.md`;
- `docs/technical_documentation.md`.

Da ricavare:

- contesto WLDT;
- problema;
- obiettivi;
- contributi;
- organizzazione della tesi.

## Capitolo 2 — Contesto tecnologico e formulazione del problema

Materiali principali:

- `06_tesi/bozze/02_contesto_tecnologico.md`;
- `00_materiali/openapi.yaml`;
- `04_progettazione/integrazione_wldt.md`;
- `04_progettazione/tecnologie.md`;
- `00_materiali/lista_repository.md`.

Da ricavare:

- Persistence Service;
- API REST;
- OpenAPI;
- LLM;
- Ollama;
- Qwen3 8B;
- FastAPI;
- vincoli dell'architettura WLDT.

## Capitolo 3 — Metodologia sperimentale e scelte progettuali

Materiali principali:

- esperimenti E001–E010;
- `02_esperimenti/benchmark_v1.md`;
- `02_esperimenti/benchmark_v2.md`;
- `03_risultati/metodologia_valutazione.md`;
- `03_risultati/confronto_modelli.md`;
- `01_appunti/decisioni_tecniche.md`.

Da ricavare:

- costruzione dei primi casi di test;
- confronto tra modelli;
- confronto tra forme differenti del contesto;
- problemi osservati con OpenAPI completa;
- motivazione della selezione delle candidate;
- distinzione tra benchmark esplorativi e valutazione successiva della pipeline.

Gli esperimenti storici non devono essere reinterpretati retroattivamente in funzione della soluzione finale.

## Capitolo 4 — Progettazione e implementazione dell'Agent Service

Materiali principali:

- `04_progettazione/architettura_agente.md`;
- `04_progettazione/formato_output_LLM.md`;
- `04_progettazione/validazione.md`;
- `05_codice/agent_service/`;
- `docs/technical_documentation.md`;
- `01_appunti/decisioni_tecniche.md`;
- `06_tesi/bozze/03_validazione_affidabilita.md`.

Il percorso:

`05_codice/agent/`

rappresenta invece il prototipo storico e deve essere utilizzato soltanto per descrivere l'evoluzione del progetto quando realmente utile alla narrazione.

Da ricavare:

- OpenApiLoader;
- OpenApiCatalog;
- ApiSelector;
- PromptBuilder;
- OllamaClient;
- GeneratedApiCall;
- gestione di missingInformation;
- ApiCallValidator;
- ApiRequestPreparer;
- RestClient;
- FastAPI;
- configurazione;
- test;
- Dockerfile.

## Capitolo 5 — Integrazione, valutazione e discussione

Materiali principali:

- `02_esperimenti/pipeline_finale/`;
- benchmark controllato del 10/08/2026;
- `docs/technical_documentation.md`;
- `01_appunti/diario_tesi.md`;
- `01_appunti/decisioni_tecniche.md`;
- modifiche al frontend nel branch `tesi/Natural-Language-Agent`;
- modifiche infrastrutturali nel branch `tesi/Agent-Service-Integration`.

Risultati già disponibili:

- integrazione Agent Service → Persistence Service reale;
- containerizzazione dell'Agent Service;
- integrazione nello stack Docker WLDT;
- networking Docker-to-Docker;
- integrazione della modalità Natural Language nel Query Workbench;
- Route Handler Next.js per la comunicazione con l'Agent Service;
- verifica browser → Agent Service → Persistence Service → MongoDB → browser;
- benchmark controllato della pipeline implementata.

Da completare in una fase successiva:

- valutazione su un insieme di richieste indipendente dai casi utilizzati durante lo sviluppo;
- discussione complessiva dei risultati;
- analisi sistematica dei limiti.

Il benchmark controllato già eseguito non deve essere presentato come valutazione held-out.

## Capitolo 6 — Conclusioni e sviluppi futuri

Da redigere dopo la valutazione finale.

Dovrà distinguere chiaramente:

- risultati effettivamente misurati;
- risultati osservati nei test di integrazione;
- limiti sperimentali;
- limiti implementativi;
- possibili estensioni future.

## Stato al 12/08/2026

Implementazione funzionale principale:

**completata e verificata end-to-end**

Attività ancora aperte:

1. eventuali feedback di relatrice e coordinatore;
2. valutazione finale indipendente;
3. stesura definitiva della tesi;
4. eventuali correzioni emerse durante la revisione.