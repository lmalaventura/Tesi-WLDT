# Diario di lavoro della tesi

## 28/07/2026

### Obiettivo

Riprendere il lavoro sulla tesi, preparare l'ambiente locale e avviare gli
esperimenti di comprensione del contratto OpenAPI tramite LLM.

### Attività svolte

- Preparata la struttura locale della tesi.
- Recuperate le repository aggiornate disponibili.
- Verificato il funzionamento del frontend e individuato il Query Workbench.
- Eseguito E001 sulla comprensione dell'OpenAPI.
- Definito il benchmark NL → API ed eseguito E002 con ChatGPT.
- Installati Ollama e Qwen3 4B.
- Eseguito E003 con modello locale.

### Risultati

Qwen3 4B non ha utilizzato correttamente la sezione `paths` del contratto e ha
prodotto endpoint e strutture non presenti.

### Prossimo passo

Ripetere il benchmark con Qwen3 8B mantenendo invariata la metodologia.

## 29/07/2026

### Obiettivo

Confrontare modelli locali e verificare l'effetto della rappresentazione del
contesto API.

### Attività svolte

- Completata la valutazione di E003.
- Eseguiti E004 con Qwen3 8B ed E005 con Llama 3.1 8B.
- Eseguito E006 con OpenAPI minimale.
- Eseguito E007 con un singolo endpoint.
- Eseguito E008 con una descrizione sintetica dei path.
- Avviata la progettazione dell'architettura dell'agente.

### Risultati

- I modelli locali hanno fallito il grounding sui path con OpenAPI completa e
  con la versione minimale che conservava gli schemi.
- Nelle esecuzioni diagnostiche E007 ed E008 Qwen3 8B ha selezionato
  correttamente gli endpoint forniti in forma isolata o sintetica.

### Decisione

Introdurre una fase preliminare di selezione delle API candidate prima della
generazione della chiamata.

### Prossimo passo

Progettare e implementare la prima pipeline locale.

## 30/07/2026

### Obiettivo

Passare dalla sperimentazione alla prima implementazione del prototipo.

### Attività svolte

- Definiti architettura, formato JSON dell'output e strategia di validazione.
- Scelto Python come linguaggio del prototipo.
- Implementati `ApiEndpoint`, `ApiCall`, `ApiSelector` e `PromptBuilder`.
- Integrato Ollama tramite API HTTP locale.
- Configurato l'output strutturato tramite JSON Schema.
- Implementato un primo `ApiCallValidator`.
- Implementato un client che prepara le richieste HTTP senza inviarle.
- Creati test automatici per selezione, prompt, validazione e preparazione REST.

### Risultati

Il prototipo riceve una richiesta naturale, seleziona un endpoint candidato,
interroga Qwen3 8B, riceve un JSON strutturato e distingue tra output valido e
richiesta eseguibile. La suite deterministica viene eseguita senza errori.

### Limiti

- Catalogo degli endpoint e regole di selezione codificati manualmente.
- Validazione limitata ad alcuni endpoint.
- OpenAPI non caricata dinamicamente.
- Nessuna esecuzione reale sul Persistence Service.
- Nessuna interfaccia HTTP o integrazione frontend.

### Prossimo passo

Confrontare un modello più grande, valutare i framework agentici e definire
l'integrazione con il sistema WLDT.

## 31/07/2026

### Obiettivo

Concludere il confronto preliminare tra modelli e definire la proposta
d'integrazione.

### Attività svolte

- Installato e testato Qwen3 14B tramite Ollama.
- Eseguito E009 con lo stesso input dei benchmark completi.
- Confrontati Qwen3 4B, Qwen3 8B, Qwen3 14B e Llama 3.1 8B.
- Analizzati LangChain, smolagents e pipeline personalizzata.
- Analizzate le repository del frontend e del Persistence Service.
- Ricostruito il flusso tra frontend Next.js, backend Kotlin/Ktor e MongoDB.
- Redatto `04_progettazione/integrazione_wldt.md`.

### Risultati

Qwen3 14B ha richiesto circa 12 minuti e quasi tutta la RAM disponibile senza
migliorare il grounding sull'OpenAPI completa. È stata proposta una pipeline
Python separata dal frontend e dal backend WLDT.

L'analisi del codice del Persistence Service ha inoltre evidenziato una
differenza tra contratto e implementazione: `/query/event/values/history`
ignora l'intervallo temporale, mentre `/query/event/values/valuesByName` lo
applica. Questa differenza deve essere considerata nell'implementazione finale
senza modificare retroattivamente gli input degli esperimenti già eseguiti.

### Prossimo passo

Inviare al coordinatore benchmark, architettura e proposta d'integrazione e
richiedere conferma delle scelte principali.

## 03/08/2026

### Obiettivo

Recepire il feedback del coordinatore, revisionare il materiale prodotto e
preparare l'avvio dell'Agent Service.

### Attività svolte

- Ricevuta conferma dell'architettura con servizio Python separato.
- Ricevuta conferma della possibilità di usare una pipeline personalizzata,
  purché motivata e testata.
- Chiarito che l'agente deve anche eseguire la richiesta sul Persistence
  Service e inoltrare il risultato al client.
- Confermata l'aggiunta di una scheda nel Query Workbench.
- Registrato il requisito di mantenere l'Agent Service allineato alla versione
  aggiornata dell'OpenAPI.
- Eseguito un checkpoint di coerenza su documentazione, benchmark e prototipo.
- Corretti errori nelle valutazioni e uniformati i risultati numerici.
- Preparata la struttura da condividere tramite repository GitHub privata.

### Risultati

La fase sperimentale e la proposta architetturale sono ora documentate in modo
coerente. Restano da ottenere il collegamento alla repository Docker e da
implementare l'Agent Service con caricamento dinamico dell'OpenAPI.

### Prossimo passo

Condividere il materiale con il coordinatore e creare lo scheletro HTTP
dell'Agent Service.

## 03/08/2026

### Attività svolte

- Revisionato e consolidato il materiale documentale prodotto durante la
  fase sperimentale.
- Inviati al relatore benchmark, progettazione, proposta d'integrazione e
  prototipo preliminare.
- Creata una repository GitHub privata per il progetto di tesi.
- Inizializzato l'Agent Service Python tramite FastAPI.
- Implementati gli endpoint `GET /health` e `POST /query`.
- Implementato il caricamento dinamico della specifica OpenAPI esposta dal
  Persistence Service.
- Implementato un catalogo normalizzato delle operazioni REST presenti nella
  specifica.
- Aggiunti test automatici per API HTTP, caricamento OpenAPI e costruzione
  del catalogo.

### Risultati

L'Agent Service dispone ora di una base HTTP funzionante e non dipende da una
copia statica della specifica OpenAPI.

La specifica viene recuperata dall'indirizzo configurato del Persistence
Service e trasformata in un catalogo interno contenente metodi HTTP, path,
descrizioni, parametri obbligatori e presenza del request body.

Questa soluzione riduce il rischio che un aggiornamento del Persistence
Service renda l'agente incompatibile con il contratto API corrente.

### Prossimo passo

Implementare la selezione degli endpoint candidati a partire dal catalogo
OpenAPI, integrando e correggendo il componente `ApiSelector` sviluppato nel
prototipo sperimentale.

## 04/08/2026

### Attività svolte

- Implementato un selettore deterministico delle operazioni API candidate.
- Collegata la selezione al catalogo OpenAPI generato dinamicamente.
- Introdotta la normalizzazione delle richieste in linguaggio naturale.
- Aggiunto un lessico di corrispondenza tra termini italiani e metadati
  tecnici dell'OpenAPI.
- Collegato il selettore all'endpoint `POST /query`.
- Aggiunti test sulle cinque richieste principali del benchmark.
- Documentato il funzionamento e i limiti della selezione.
- Definita la prima struttura provvisoria dei capitoli della tesi.
- Avviata la stesura personale dell'introduzione e degli obiettivi.

### Risultati

L'endpoint `POST /query` non restituisce più una risposta simulata, ma carica
la specifica OpenAPI corrente, costruisce il catalogo delle operazioni e
restituisce i candidati maggiormente coerenti con la richiesta ricevuta.

La selezione rimane deterministica e osservabile: per ogni candidato vengono
restituiti il punteggio e i termini che hanno contribuito alla scelta.

Il modello LLM non è ancora collegato. Il passaggio successivo consisterà
nella costruzione di un prompt contenente soltanto le operazioni candidate.

### Prossimo passo

Implementare il PromptBuilder e l'OllamaClient, definire lo schema JSON della
chiamata generata e collegare il primo modello locale all'Agent Service.

## 05/08/2026

### Attività svolte

- Implementato il `PromptBuilder`.
- Limitato il prompt alle operazioni candidate e agli schemi OpenAPI
  effettivamente referenziati.
- Definito il modello `GeneratedApiCall`.
- Implementato il client HTTP per la Chat API di Ollama.
- Configurata la generazione mediante JSON Schema.
- Disabilitati streaming e thinking per la risposta elaborata dal servizio.
- Collegato Ollama all'endpoint `POST /query`.
- Aggiunti test per costruzione del prompt, parsing e validazione dell'output.
- Eseguiti tre smoke test reali con Qwen3 8B:
- elenco dei Digital Twin, completato correttamente;
- recupero dello snapshot mediante path parameter, completato correttamente;
- interrogazione storica per intervallo, corretta nella scelta dell’endpoint
  ma non nella struttura del request body.
- Avviata la bozza sul contesto tecnologico della tesi.

### Risultati

L’Agent Service è in grado di trasformare la richiesta naturale e le
operazioni candidate in un prompt ristretto, inviarlo a Qwen3 8B tramite
Ollama e ottenere una chiamata REST conforme alla struttura generale
`GeneratedApiCall`.

Le richieste relative all’elenco dei Digital Twin e allo snapshot corrente
sono state tradotte correttamente.

Nel caso dell’interrogazione storica con intervallo temporale, il modello ha
selezionato correttamente l’endpoint
`POST /query/event/values/valuesByName`, ma ha prodotto un oggetto al posto
dell’array previsto dal request body e ha utilizzato `propertyId` invece di
`propertyName`.

Il test conferma che la generazione strutturata deve essere seguita da una
validazione semantica completa rispetto alla specifica OpenAPI.

### Prossimo passo

Implementare la validazione completa della chiamata generata, distinguere
informazioni mancanti ed errori del modello e collegare il `RestClient` per
l'invio al Persistence Service.

## 06/08/2026

### Attività svolte

- Implementato il validatore deterministico delle chiamate generate.
- Verificata la corrispondenza tra metodo, endpoint e operazioni candidate.
- Introdotti i controlli sui path parameter e sui query parameter.
- Implementata la validazione del request body rispetto agli schemi OpenAPI.
- Gestita la risoluzione dei riferimenti locali `$ref`.
- Aggiunti controlli su oggetti, array, tipi, enumerazioni e date-time.
- Introdotta la distinzione semantica tra operazioni `byName` e `byId`.
- Collegato il validatore all'endpoint `POST /query`.
- Bloccati gli output semanticamente non validi prima dell'esecuzione.
- Eseguiti smoke test reali con Qwen3 8B.
- Verificata una chiamata valida relativa all'elenco dei Digital Twin.
- Verificato il rifiuto della chiamata storica con body non conforme.
- Aggiunta la dipendenza di sviluppo `httpx2` per rimuovere il warning del
  `TestClient`.
- Implementato l'`ApiRequestPreparer`.
- Aggiunta la sostituzione e la codifica sicura dei path parameter.
- Separata la preparazione della richiesta dalla futura esecuzione HTTP.
- Portata la suite automatica a 32 test senza warning.
- Avviata la bozza della tesi sulla validazione e sull'affidabilità.

### Risultati

Una chiamata generata dal modello viene ora considerata utilizzabile soltanto
se metodo ed endpoint corrispondono a una delle operazioni candidate e se
parametri e request body rispettano la specifica OpenAPI corrente.

La richiesta relativa all'elenco dei Digital Twin ha prodotto la chiamata
`GET /hdts`, che ha superato correttamente la validazione.

Lo smoke test storico, che in precedenza produceva un falso risultato `200`,
è stato correttamente bloccato con errore `502`. Il validatore ha rilevato
sia l'impiego di un oggetto al posto dell'array previsto sia l'utilizzo di
`propertyId` al posto di `propertyName`.

Le chiamate valide possono inoltre essere trasformate in richieste HTTP
concrete. L'`ApiRequestPreparer` combina il base URL con il path, sostituisce
i placeholder e conserva separatamente query parameter e request body.

La richiesta risultante non viene ancora eseguita verso il Persistence
Service.

### Prossimo passo

Implementare il `RestClient`, utilizzare le richieste prodotte
dall'`ApiRequestPreparer` ed eseguire la chiamata HTTP soltanto dopo il
superamento della validazione.

Successivamente dovranno essere gestiti status code, contenuto e possibili
errori restituiti dal Persistence Service.

## 09/08/2026

### Attività svolte

- Implementato il `RestClient`.
- Collegata l'esecuzione HTTP alle richieste prodotte
  dall'`ApiRequestPreparer`.
- Gestiti separatamente query parameter e request body.
- Implementata la lettura delle risposte JSON del Persistence Service.
- Mantenuti gli status code restituiti dal backend.
- Distinti gli errori HTTP dagli errori di trasporto.
- Collegata l'esecuzione all'endpoint `POST /query`.
- Estesa la risposta dell'Agent Service con richiesta preparata e risposta
  del Persistence Service.
- Aggiunti test unitari del `RestClient`.
- Aggiunti test di orchestrazione dell'intera pipeline.
- Portata la suite automatica a 38 test.
- Verificato il comportamento in caso di Persistence Service non
  raggiungibile.

### Risultati

La pipeline dell'Agent Service è ora completa dal punto di vista
dell'orchestrazione:

richiesta naturale
→ caricamento OpenAPI
→ selezione dei candidati
→ generazione mediante LLM
→ validazione deterministica
→ preparazione della richiesta HTTP
→ esecuzione tramite `RestClient`
→ restituzione della risposta al client.

Il comportamento positivo dell'esecuzione è verificato attraverso test con
un Persistence Service simulato.

L'esecuzione contro l'ambiente WLDT reale rimane dipendente dalla
disponibilità dell'infrastruttura necessaria.

### Prossimo passo

Eseguire un benchmark della pipeline completa, consolidare la
documentazione tecnica e verificare l'integrazione reale appena sarà
disponibile l'ambiente WLDT.

Valutare inoltre l'integrazione minima dell'Agent Service nel Query
Workbench del frontend.