# Decisioni tecniche

Registro delle decisioni progettuali assunte durante la tesi. Ogni voce indica
il problema affrontato, la soluzione adottata e la motivazione disponibile al
momento della decisione.

## Benchmark sperimentale — 28/07/2026

È stato definito un benchmark composto da cinque richieste in linguaggio
naturale. Nei benchmark completi vengono mantenuti invariati il prompt, le
richieste e i criteri di valutazione. Gli esperimenti diagnostici E007 ed E008
misurano invece soltanto la selezione dell'endpoint e non sono direttamente
confrontabili con i punteggi su 50.

## Rappresentazione delle API — 29/07/2026

### Problema

Qwen3 8B non ha individuato con affidabilità i path quando ha ricevuto la
specifica OpenAPI completa o una versione minimale che conservava gli schemi.

### Evidenze considerate

- E004: OpenAPI completa;
- E006: OpenAPI minimale con schemi;
- E007: un solo endpoint;
- E008: cinque descrizioni sintetiche dei path.

### Decisione

Introdurre una fase preliminare di selezione delle operazioni candidate e
fornire al modello una rappresentazione compatta delle sole operazioni
rilevanti.

### Limite dell'evidenza

E007 ed E008 sono esecuzioni diagnostiche singole. Indicano una direzione
progettuale, ma non dimostrano da sole un miglioramento statisticamente
significativo.

## Linguaggio del prototipo — 30/07/2026

È stato scelto Python per isolare la logica LLM dal frontend TypeScript e dal
Persistence Service Kotlin. La scelta consente inoltre di comunicare con
Ollama e con i servizi HTTP senza introdurre modifiche nei componenti WLDT
esistenti.

## Prima struttura del prototipo — 30/07/2026

Il prototipo è stato suddiviso in:

- `models.py`: strutture dati;
- `api_selector.py`: selezione deterministica di un insieme limitato di endpoint;
- `prompt_builder.py`: costruzione del contesto compatto e dello schema JSON;
- `ollama_client.py`: comunicazione con Ollama;
- `validator.py`: validazione preliminare dell'output;
- `rest_client.py`: preparazione della richiesta HTTP;
- `main.py`: coordinamento della pipeline.

Il catalogo delle API e parte della validazione sono ancora codificati
manualmente. Questa versione serve a verificare il flusso e non rappresenta
l'implementazione definitiva.

## Output strutturato e validazione — 30/07/2026

L'output del modello viene vincolato con un JSON Schema passato all'API di
Ollama. Il validatore distingue tra:

- output strutturalmente valido;
- richiesta eseguibile;
- richiesta bloccata perché mancano informazioni obbligatorie.

La copertura attuale del validatore è parziale e deve essere sostituita da una
validazione derivata dalla specifica OpenAPI aggiornata.

## Strategia di testing — 30/07/2026

I componenti deterministici vengono verificati con `unittest`. L'invocazione
di Ollama e l'esecuzione sul Persistence Service restano test di integrazione
separati. Al checkpoint del 3 agosto la suite comprende 18 test e risulta
completamente superata.

## Scelta della pipeline — 31/07/2026, confermata il 03/08/2026

Sono stati considerati LangChain, smolagents e una pipeline personalizzata.
Il coordinatore ha confermato che la pipeline personalizzata è accettabile se
la scelta viene motivata e testata.

La motivazione non è che i framework esistenti non possano realizzare il
flusso richiesto. Il vantaggio atteso è l'attinenza allo scope: il caso d'uso
prevede una sequenza deterministica, un insieme di API controllato, una sola
chiamata LLM e una validazione obbligatoria prima dell'esecuzione. Non sono al
momento richiesti pianificazione autonoma, memoria conversazionale o cicli
multi-step generici.

Non è ancora disponibile un confronto empirico delle prestazioni tra le tre
soluzioni; pertanto non viene rivendicato un vantaggio prestazionale.

## Architettura d'integrazione — 03/08/2026

L'agente verrà realizzato come servizio Python separato. Il servizio riceverà
la richiesta naturale, selezionerà l'operazione, genererà e validerà i
parametri, eseguirà la richiesta sul Persistence Service e inoltrerà la
risposta al client.

Il frontend verrà esteso con una scheda nel Query Workbench. La prima versione
prevede almeno una casella di testo e una tabella dei risultati.

## Allineamento della specifica OpenAPI — 03/08/2026

L'Agent Service non deve dipendere da una copia locale aggiornata manualmente.
La specifica usata per selezione e validazione verrà recuperata dal
Persistence Service tramite `GET /openapi.yaml`, in modo che i due componenti
utilizzino lo stesso contratto. Devono essere definite la politica di refresh
e la gestione dell'indisponibilità del servizio.
