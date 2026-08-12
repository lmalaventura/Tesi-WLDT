# Struttura provvisoria della tesi

## Titolo provvisorio

**Progettazione e implementazione di un agente LLM per la traduzione di richieste in linguaggio naturale in chiamate REST nel sistema WLDT**

Il lavoro effettivamente svolto riguarda la trasformazione NL → REST guidata dalla specifica OpenAPI del Persistence Service, e non una traduzione NL → SQL.

## Capitolo 1 — Introduzione

Introduce il contesto generale del lavoro e definisce il problema affrontato.

- contesto del sistema WLDT;
- modalità di interrogazione del Persistence Service;
- problema della traduzione da linguaggio naturale a chiamate API;
- obiettivi della tesi;
- contributi principali;
- organizzazione del documento.

## Capitolo 2 — Contesto tecnologico e formulazione del problema

Descrive le tecnologie e i vincoli necessari per comprendere le scelte successive.

- architettura essenziale di WLDT;
- ruolo del Persistence Service;
- API REST e specifica OpenAPI;
- Large Language Model e inferenza locale;
- Ollama e Qwen3 8B;
- Agent Service e comunicazione HTTP;
- requisiti e vincoli derivanti dall'infrastruttura esistente;
- rischi legati alla generazione di chiamate non conformi al contratto API.

## Capitolo 3 — Metodologia sperimentale e scelte progettuali

Descrive gli esperimenti che hanno preceduto l'implementazione e mostra come i risultati abbiano influenzato la progettazione della soluzione.

- definizione del benchmark esplorativo;
- richieste utilizzate;
- modelli linguistici confrontati;
- diverse modalità di rappresentazione del contesto OpenAPI;
- criteri e metodologia di valutazione;
- risultati degli esperimenti preliminari;
- limiti osservati nell'utilizzo diretto dell'OpenAPI completa;
- motivazione della selezione preventiva delle operazioni candidate;
- confronto concettuale con approcci agentici più generali;
- motivazione della pipeline specifica per WLDT.

Gli esperimenti esplorativi utilizzati durante la progettazione verranno distinti dalla successiva valutazione della pipeline implementata.

## Capitolo 4 — Progettazione e implementazione dell'Agent Service

Descrive l'architettura della soluzione e la sua realizzazione.

- estensione dell'architettura WLDT;
- caricamento dinamico della specifica OpenAPI;
- costruzione del catalogo delle operazioni;
- selezione deterministica delle operazioni candidate;
- costruzione del prompt;
- utilizzo di Qwen3 8B tramite Ollama;
- formato strutturato `GeneratedApiCall`;
- gestione delle informazioni mancanti;
- validazione deterministica rispetto alla OpenAPI;
- preparazione ed esecuzione della richiesta REST;
- organizzazione dell'Agent Service in FastAPI;
- configurazione del servizio;
- test automatici;
- containerizzazione tramite Docker.

## Capitolo 5 — Integrazione, valutazione e discussione

Verifica il comportamento della soluzione nel sistema WLDT reale e discute i risultati ottenuti.

- integrazione dell'Agent Service nello stack Docker di sviluppo;
- comunicazione con Ollama e Persistence Service;
- integrazione nel Query Workbench;
- modalità Natural Language;
- comunicazione frontend → Agent Service tramite Next.js;
- test end-to-end sul sistema reale;
- benchmark controllato della pipeline implementata;
- successiva valutazione su richieste indipendenti dai casi utilizzati durante lo sviluppo;
- analisi degli errori;
- limiti metodologici e implementativi;
- discussione dei risultati.

Il benchmark controllato già eseguito verrà mantenuto distinto dalla valutazione finale indipendente.

## Capitolo 6 — Conclusioni e sviluppi futuri

- sintesi dei risultati;
- verifica degli obiettivi iniziali;
- principali contributi;
- limiti della soluzione;
- possibili miglioramenti della metodologia di valutazione;
- possibili estensioni dell'Agent Service e dell'integrazione WLDT.