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


## 10/08/2026

### Obiettivo

Completare la prima implementazione end-to-end dell'Agent Service, verificare
la pipeline con un Persistence Service simulato e produrre un benchmark
controllato.

### Attività svolte

- Completata la pipeline `POST /query`.
- Verificato il caricamento dinamico della OpenAPI.
- Consolidato il catalogo delle operazioni.
- Migliorato il selettore deterministico.
- Impostata la selezione a un massimo di tre candidate.
- Integrato Qwen3 8B tramite Ollama.
- Configurato lo structured output.
- Impostata la temperatura a zero.
- Distinte le condizioni di indisponibilità Ollama dagli errori della risposta.
- Implementato e verificato il validatore OpenAPI.
- Implementato `ApiRequestPreparer`.
- Implementato `RestClient`.
- Collegata l'esecuzione al Persistence Service.
- Realizzato un mock del Persistence Service.
- Realizzato il runner del benchmark finale.
- Esteso lo scoring alla correttezza semantica.
- Eseguito il benchmark finale su cinque casi ripetuti tre volte.

### Problemi individuati durante la diagnostica

#### Snapshot

Il modello sostituiva inizialmente il placeholder OpenAPI:

```text
/hdts/HDT-001/snapshot
```

invece di mantenere:

```text
/hdts/{id}/snapshot
```

con il valore separato nei path parameter.

#### ValuesByName

Il modello produceva inizialmente un oggetto come body anziché l'array richiesto
dalla OpenAPI.

In una fase successiva utilizzava `propertyId` al posto di `propertyName`.

Sono stati introdotti vincoli coerenti con l'operazione candidata.

#### Statistiche

Il modello ometteva inizialmente:

```text
hdtIds
modelIds
modelNames
```

nonostante fossero obbligatori nello schema.

Lo structured output è stato esteso per mantenere i campi obbligatori e il
prompt specifica l'utilizzo degli array vuoti in assenza del relativo filtro.

#### Riferimenti OpenAPI

La propagazione dei `$ref` OpenAPI nello schema inviato a Ollama produceva
errori.

I riferimenti non risolvibili sono stati rimossi dallo schema autonomo di
structured output.

### Benchmark finale

Configurazione:

```text
5 casi
3 ripetizioni
15 esecuzioni
Qwen3 8B
Ollama
Persistence Service simulato
```

Risultato:

```text
Operation accuracy: 80%
Arguments accuracy: 60%
Semantic accuracy: 60%
Validation pass rate: 80%
Execution success rate: 80%
End-to-end success rate: 60%
Tempo medio: 25.731 s
```

### Risultati per caso

```text
Q1: 0/3 end-to-end
Q2: 3/3 end-to-end
Q3: 3/3 end-to-end
Q4: 0/3 end-to-end
Q5: 3/3 end-to-end
```

Q1 genera `POST /hdts` invece di `GET /hdts` e produce un body non richiesto.
Il validatore impedisce l'esecuzione.

Q4 seleziona correttamente `/query/event/comparison`, ma utilizza `GTE` invece
di `GT`.

Il caso mostra la differenza tra validità OpenAPI e correttezza semantica.

### Decisione

Il benchmark viene congelato nello stato attuale.

Non vengono introdotte altre modifiche all'agente specificamente per correggere
Q1 e Q4 sui casi già utilizzati.

### Prossimi passi

- riallineare la documentazione tecnica;
- preparare il materiale da condividere con il relatore;
- verificare l'agente sul Persistence Service reale quando disponibile;
- integrare successivamente il servizio nel Query Workbench;
- valutare eventualmente un nuovo set di richieste indipendenti.

## 11/08/2026

### Feedback del relatore

Ricevuto un nuovo feedback dal relatore.

La proposta di estensione dell'architettura è stata valutata positivamente ed è
stata considerata positiva anche la scelta di mantenere traccia degli
esperimenti e del processo di valutazione.

Il relatore ha chiesto di:

- condividere la repository GitHub del progetto;
- mantenere codice e documentazione organizzati;
- predisporre un documento tecnico unico;
- organizzare tale documento nelle sezioni `Context`, `Design` e `Validation`;
- continuare per il momento con l'attuale impostazione sperimentale, in attesa
  di eventuali indicazioni successive su una metodologia di valutazione più
  strutturata.

Per l'integrazione con WLDT è stato inoltre suggerito l'utilizzo della
configurazione development contenuta nella repository `whdt-monitor-infra`.

Questa configurazione permette di costruire i servizi direttamente dalle
repository locali e rende possibile aggiungere successivamente anche il nuovo
Agent Service Python allo stack.

### Preparazione dell'ambiente WLDT

Sono state clonate localmente, sotto una stessa directory, le repository:

```text
whdt-monitor-frontend
persistence-service
hdt-creation-service
whdt-monitor-infra
```

La struttura locale utilizzata è:

```text
C:\Users\x\Desktop\WLDT-dev\
├── whdt-monitor-frontend\
├── persistence-service\
├── hdt-creation-service\
└── whdt-monitor-infra\
```

Per poter utilizzare lo stack è stato installato Docker Desktop e aggiornato
WSL 2.

Dopo l'installazione sono stati verificati con successo:

```text
docker version
docker compose version
docker info
```

### Problema con gradlew durante la prima build

Il primo tentativo di build dello stack development falliva sia per il
Persistence Service sia per l'HDT Creation Service durante:

```text
RUN ./gradlew buildFatJar --no-daemon
```

con errore:

```text
/bin/sh: ./gradlew: not found
```

È stato verificato che:

- `gradlew` era presente;
- `gradlew` era tracciato da Git;
- il Gradle Wrapper era completo;
- `.dockerignore` non escludeva il file;
- il file risultava eseguibile nel repository.

Il controllo dei line ending ha mostrato però:

```text
i/lf w/crlf
```

quindi il file archiviato da Git era LF, mentre il working tree Windows lo
aveva convertito in CRLF.

La configurazione Git locale dei repository `persistence-service` e
`hdt-creation-service` è stata modificata in modo da non effettuare questa
conversione.

Dopo il ripristino di `gradlew`, il working tree risultava nuovamente LF e la
build Docker ha potuto proseguire.

Non sono stati modificati i Dockerfile ufficiali per compensare artificialmente
il problema.

### Avvio dello stack development WLDT

Lo stack è stato avviato utilizzando la configurazione development:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

La configurazione costruisce dai repository locali:

```text
persistence-service
hdt-creation-service
whdt-monitor-frontend
```

e avvia inoltre MongoDB.

Le principali porte utilizzate localmente sono:

```text
3000 → whdt-monitor-frontend
8080 → hdt-creation-service
8081 → persistence-service
```

L'Agent Service della tesi è stato mantenuto inizialmente fuori da Docker.

Questa scelta permette di verificare prima:

```text
Agent Service su host
→ Persistence Service in Docker
```

senza introdurre contemporaneamente eventuali problemi di networking
container-to-container.

### Collegamento dell'Agent Service alla OpenAPI reale

L'Agent Service è stato configurato per utilizzare il Persistence Service reale
in esecuzione localmente.

La specifica OpenAPI è stata recuperata da:

```text
http://127.0.0.1:8081/openapi.yaml
```

La verifica:

```text
GET /health
```

ha restituito correttamente lo stato `ok`.

La verifica:

```text
GET /openapi/status
```

ha mostrato:

```text
status = ok
source = http://127.0.0.1:8081/openapi.yaml
OpenAPI version = 3.1.1
path count = 26
```

La verifica:

```text
GET /openapi/operations
```

ha prodotto un catalogo di:

```text
37 operazioni
```

L'Agent Service è quindi riuscito a costruire dinamicamente il proprio catalogo
a partire dalla specifica reale del Persistence Service.

### Primo smoke test sul Persistence Service reale

Prima di creare dati nel database è stata utilizzata una richiesta che non
richiedesse un HDT esistente:

```text
Mostrami i nomi distinti delle proprietà disponibili.
```

La richiesta è stata inviata a:

```text
POST /query
```

dell'Agent Service.

Il selettore ha incluso tra le candidate:

```text
GET /properties/names
```

e il modello Qwen3 8B ha generato:

```text
method = GET
endpoint = /properties/names
pathParameters = {}
queryParameters = {}
body = null
missingInformation = []
```

La chiamata ha superato la validazione:

```text
valid = true
```

ed è stata preparata come:

```text
GET http://127.0.0.1:8081/properties/names
```

Il Persistence Service reale ha restituito:

```text
HTTP 200
```

Il database non conteneva ancora Digital Twin, quindi il body restituito era un
array vuoto.

Il test ha comunque verificato per la prima volta la sequenza:

```text
richiesta in linguaggio naturale
→ Agent Service
→ OpenAPI reale
→ selezione candidate
→ Qwen3 8B
→ GeneratedApiCall
→ validazione
→ richiesta REST
→ Persistence Service reale
```

### Analisi del flusso JSON del frontend

Per creare un HDT coerente con il normale funzionamento di WLDT è stato
analizzato il flusso JSON del frontend invece di inserire direttamente dati nel
Persistence Service.

Il componente `HdtManager.tsx` accetta:

```text
un oggetto JSON
oppure
un array di oggetti JSON
```

Il frontend normalizza l'input in un array e invia:

```text
POST /api/creation/hdts/json/batch
```

all'HDT Creation Service.

La validazione effettiva degli elementi viene delegata al backend.

### Analisi del JSON richiesto dal Creation Service

Nel Creation Service è stato analizzato `JsonDomainAssembler`.

Per ogni elemento vengono richiesti obbligatoriamente:

```text
ID
Age
task
Sex
```

con:

```text
ID   → valore primitivo/stringa
Age  → numero
task → valore primitivo/stringa
Sex  → valore primitivo/stringa
```

Gli ulteriori campi primitivi presenti nell'oggetto vengono convertiti in
proprietà del Digital Twin.

Per ciascuna proprietà viene inoltre creata un'osservazione iniziale.

### Creazione di TEST-001

È stato quindi creato attraverso il normale flusso JSON del frontend il seguente
HDT:

```json
{
  "ID": "TEST-001",
  "Age": 30,
  "task": "rest",
  "Sex": "M",
  "heartRate": 72,
  "systolicPressure": 120
}
```

Dopo l'importazione:

```text
GET /hdts
```

ha restituito un HDT con:

```text
hdtId = TEST-001
```

confermando la memorizzazione nel Persistence Service reale.

### Verifica diretta dello snapshot

Prima di utilizzare nuovamente l'Agent Service è stato interrogato direttamente:

```text
GET /hdts/TEST-001/snapshot
```

La richiesta ha restituito:

```text
HTTP 200
```

e il body conteneva:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

Per tutti i valori la sorgente indicata dal Persistence Service era:

```text
source = observation
```

Le osservazioni erano state create durante il processo di ingestione JSON.

### Test NL-to-REST parametrizzato sul backend reale

Dopo la verifica diretta è stata inviata all'Agent Service la richiesta:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

Il selettore ha prodotto come prima candidata:

```text
GET /hdts/{id}/snapshot
```

con punteggio superiore alle altre candidate.

Qwen3 8B ha generato:

```text
method = GET
endpoint = /hdts/{id}/snapshot
pathParameters.id = TEST-001
queryParameters = {}
body = null
missingInformation = []
```

La chiamata ha superato la validazione:

```text
valid = true
```

`ApiRequestPreparer` ha quindi costruito:

```text
GET http://127.0.0.1:8081/hdts/TEST-001/snapshot
```

Il Persistence Service reale ha restituito:

```text
HTTP 200
```

L'Agent Service ha ricevuto e restituito correttamente:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

È stato quindi verificato il primo flusso completo parametrizzato:

```text
richiesta in linguaggio naturale
→ Agent Service
→ OpenAPI reale
→ ApiSelector
→ Qwen3 8B
→ GeneratedApiCall
→ ApiCallValidator
→ ApiRequestPreparer
→ RestClient
→ Persistence Service reale
→ MongoDB
→ risposta reale
```

### Comportamento osservato su GET /hdts/{id}

Durante i controlli è stato osservato un comportamento anomalo della chiamata:

```text
GET /hdts/TEST-001
```

che restituisce:

```text
HTTP 500
state should be: hexString has 24 characters
```

La chiamata:

```text
GET /hdts/TEST-001/snapshot
```

utilizzando lo stesso identificatore funziona invece correttamente e restituisce
HTTP 200.

La situazione è stata registrata come comportamento del Persistence Service.

Non è stato introdotto alcun workaround nell'Agent Service per trasformare
l'identificatore o nascondere il problema.

L'eventuale causa nel backend potrà essere analizzata separatamente.

### Separazione tra benchmark e integrazione reale

Il benchmark congelato del 10/08/2026 rimane invariato.

Il benchmark quantitativo utilizza:

```text
5 casi
3 ripetizioni
15 esecuzioni complessive
Persistence Service simulato
```

e mantiene le metriche già registrate.

Le verifiche dell'11/08/2026 hanno invece lo scopo di dimostrare
l'integrazione con l'ambiente WLDT reale.

I risultati dello smoke test reale non vengono utilizzati per modificare
retroattivamente il benchmark precedente.

Le due evidenze vengono quindi mantenute separate:

```text
10/08/2026
benchmark controllato e regressivo
→ mock Persistence Service

11/08/2026
smoke test di integrazione
→ Persistence Service WLDT reale
```

### Stato raggiunto

A fine giornata risultano verificati:

```text
Docker Desktop e WSL 2
stack development WLDT
frontend reale
HDT Creation Service reale
Persistence Service reale
MongoDB
Agent Service su host
OpenAPI reale
catalogo di 37 operazioni
generazione strutturata tramite Qwen3 8B
validazione della chiamata
esecuzione verso Persistence reale
creazione di un HDT tramite Creation Service
snapshot diretto
snapshot richiesto tramite linguaggio naturale
```

### Prossimi passi

I prossimi passi tecnici sono:

1. containerizzare `05_codice/agent_service`;
2. aggiungere l'Agent Service allo stack development;
3. configurare la comunicazione container-to-container con il Persistence
   Service;
4. configurare l'accesso a Ollama dal container;
5. ripetere lo smoke test con Agent Service e Persistence Service entrambi
   integrati nello stack;
6. integrare successivamente la modalità Natural Language nel Query Workbench.

Sul piano della valutazione:

1. mantenere congelato il benchmark del 10 agosto;
2. attendere l'eventuale proposta del relatore relativa a strumenti o
   metodologie di valutazione più strutturate;
3. progettare successivamente una valutazione su richieste indipendenti da
   quelle utilizzate durante lo sviluppo.