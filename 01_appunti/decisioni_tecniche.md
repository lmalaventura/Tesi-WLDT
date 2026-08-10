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


## Selezione deterministica delle API candidate — 04/08/2026

È stato implementato un primo selettore deterministico delle operazioni
OpenAPI.

Il selettore lavora sul catalogo generato dinamicamente dalla specifica del
Persistence Service e non utilizza un elenco statico degli endpoint.

La richiesta viene normalizzata e confrontata con path, operationId,
descrizioni, tag e parametri delle operazioni. Il risultato è una lista
ordinata di candidati associati a un punteggio e ai termini che hanno
contribuito alla selezione.

Questa fase non produce ancora la chiamata REST definitiva. Il suo scopo è
ridurre il contesto che verrà fornito al modello LLM e rendere osservabile il
processo di scelta preliminare.

## Necessità della validazione semantica — 05/08/2026

Gli smoke test hanno mostrato che un output formalmente conforme al modello
Pydantic generale può comunque risultare non conforme allo schema OpenAPI
dell’operazione selezionata.

In particolare, il modello ha prodotto un request body con una struttura
radice errata e ha confuso `propertyName` con `propertyId`, pur scegliendo
l’endpoint corretto.

È stato quindi confermato che la chiamata generata non deve mai essere
inoltrata direttamente al Persistence Service. Deve prima essere confrontata
con metodo, path, parametri e request body definiti nella specifica OpenAPI
corrente.

## Rifiuto degli output semanticamente non validi — 06/08/2026

È stato scelto di non correggere automaticamente le chiamate prodotte dal
modello linguistico.

Quando metodo, endpoint, parametri o request body non rispettano la specifica
OpenAPI, il validatore restituisce un insieme di problemi strutturati e
l'endpoint `POST /query` interrompe la pipeline con un errore `502`.

Una correzione automatica potrebbe nascondere un errore del modello oppure
alterare l'intenzione originale dell'utente. Il rifiuto mantiene invece
separate la generazione probabilistica della chiamata e la sua verifica
deterministica.

## Separazione tra validazione, preparazione ed esecuzione — 06/08/2026

La costruzione della richiesta HTTP è stata separata dalla validazione e
dalla futura esecuzione.

Il componente `ApiCallValidator` stabilisce se la chiamata generata è
compatibile con la specifica OpenAPI. Soltanto dopo il superamento di questo
controllo, l'`ApiRequestPreparer` sostituisce i placeholder del path,
codifica i relativi valori e combina l'endpoint con il base URL del
Persistence Service.

La richiesta risultante conserva separatamente metodo HTTP, URL, query
parameter e body. L'invio effettivo verrà affidato a un `RestClient`
dedicato.

Questa separazione consente di testare individualmente le diverse
responsabilità e impedisce che una chiamata non validata venga eseguita
accidentalmente.

## Aggiornamento del backend del TestClient — 06/08/2026

È stata aggiunta la dipendenza di sviluppo `httpx2` per eliminare il warning
di deprecazione prodotto dal `TestClient` di Starlette.

La dipendenza applicativa `httpx` è stata mantenuta, poiché viene utilizzata
direttamente dall'Agent Service per le comunicazioni HTTP con Ollama e con
gli altri servizi.

La modifica riguarda quindi esclusivamente l'ambiente di test e non altera
il comportamento dell'applicazione.

## Separazione tra errori HTTP e indisponibilità del backend — 09/08/2026

Il `RestClient` non trasforma automaticamente gli status code `4xx` e `5xx`
del Persistence Service in errori interni dell'Agent Service.

Una risposta HTTP ricevuta dal backend rappresenta infatti un'esecuzione
avvenuta, anche quando segnala che una risorsa non esiste o che la richiesta
non può essere soddisfatta.

L'Agent Service conserva quindi status code, content type e body della
risposta.

Gli errori di trasporto vengono gestiti separatamente. Se il Persistence
Service non è raggiungibile, l'Agent Service interrompe la pipeline con
`503 Service Unavailable`.


## Implementazione corrente separata dal prototipo — 10/08/2026

### Problema

Il codice in `05_codice/agent` rappresenta la fase sperimentale e non deve
essere confuso con l'implementazione finale.

### Decisione

Mantenere il prototipo storico e sviluppare l'implementazione corrente in:

```text
05_codice/agent_service
```

### Motivazione

La separazione preserva la cronologia sperimentale senza trasformarla
retroattivamente nell'implementazione finale.

## Caricamento dinamico della OpenAPI — 10/08/2026

### Problema

Una copia statica della specifica richiederebbe aggiornamenti manuali ad ogni
variazione del Persistence Service.

### Decisione

Recuperare la OpenAPI dall'indirizzo configurato del Persistence Service.

### Motivazione

È l'Agent Service a doversi adattare al contratto corrente del backend.

## Selezione deterministica top 3 — 10/08/2026

### Problema

Gli esperimenti preliminari hanno evidenziato difficoltà quando i modelli locali
ricevono direttamente un contesto OpenAPI troppo ampio.

### Decisione

Utilizzare un selettore deterministico che restituisce al massimo tre
operazioni candidate ordinate per punteggio.

### Motivazione

La selezione riduce il contesto senza affidare interamente al modello
l'individuazione delle operazioni nella specifica completa.

## Structured output dinamico — 10/08/2026

### Problema

Il solo prompt testuale non impediva al modello di produrre endpoint o body in
forme incompatibili con la chiamata attesa.

### Decisione

Adattare dinamicamente il JSON Schema dello structured output alle candidate
correnti.

Possono essere limitati:

- metodo;
- endpoint;
- tipo del body;
- campi obbligatori.

### Motivazione

I vincoli vengono applicati prima della generazione invece di correggere la
chiamata dopo la risposta del modello.

## Gestione dei riferimenti OpenAPI — 10/08/2026

### Problema

La propagazione diretta di riferimenti:

```text
#/components/schemas/...
```

nel JSON Schema autonomo inviato a Ollama provocava errori perché tali
riferimenti non erano risolvibili nel documento di structured output.

### Decisione

Non propagare direttamente questi `$ref` nello schema autonomo di Ollama.

Gli schemi OpenAPI completi rimangono disponibili nel prompt e nella
validazione.

## Configurazione deterministica di Ollama — 10/08/2026

### Decisione

Utilizzare Qwen3 8B con:

```text
stream = false
think = false
temperature = 0
```

### Motivazione

Il compito richiede una trasformazione strutturata e non generazione creativa.

## Validazione indipendente — 10/08/2026

### Decisione

Il validatore non corregge automaticamente a posteriori la chiamata prodotta
dal modello.

### Motivazione

Il controllo deve rimanere indipendente dalla generazione e deve rendere
osservabili gli errori invece di nasconderli tramite correzioni automatiche.

## Benchmark semantico — 10/08/2026

### Problema

Valutare soltanto metodo ed endpoint può classificare come corretta una
chiamata formalmente indirizzata all'operazione giusta ma semanticamente
diversa dalla richiesta.

### Decisione

Misurare separatamente:

```text
operation_correct
arguments_correct
semantic_correct
validation_valid
execution_success
end_to_end_success
```

### Motivazione

Nel caso Q4 il modello genera `GTE`, valido secondo OpenAPI, al posto di `GT`.

## Congelamento del benchmark — 10/08/2026

### Decisione

Dopo tre ripetizioni dei cinque casi, congelare il risultato senza modificare
ulteriormente l'agente specificamente sui fallimenti osservati.

### Risultato

```text
15 esecuzioni
operation accuracy: 80%
semantic accuracy: 60%
validation pass: 80%
execution success: 80%
end-to-end success: 60%
```

### Motivazione

Correggere ulteriormente l'agente sui cinque casi già utilizzati avrebbe
adattato manualmente il sistema al benchmark.

Eventuali miglioramenti successivi dovranno essere valutati separatamente.