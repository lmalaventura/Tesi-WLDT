# Technical Documentation

## Context

### WLDT current architecture

WLDT è organizzato come un insieme di servizi separati.

Nell'ambiente di sviluppo utilizzato per questa tesi lo stack principale è
costituito da:

```text
whdt-monitor-frontend
        ↓
hdt-creation-service
        ↓
persistence-service
        ↓
MongoDB
```

Il frontend fornisce le funzionalità di monitoraggio, interrogazione e
ingestione dei dati.

L'HDT Creation Service gestisce i flussi di importazione e costruzione dei
Digital Twin a partire da sorgenti quali Excel, JSON e Sensor CSV.

Il Persistence Service espone invece le API REST utilizzate per memorizzare e
interrogare HDT, modelli, proprietà, osservazioni e viste.

### Problem addressed

L'accesso alle funzionalità del Persistence Service richiede normalmente che il
client conosca la struttura delle API disponibili, tra cui:

- endpoint;
- metodo HTTP;
- path parameter;
- query parameter;
- struttura del request body;
- vincoli definiti dal contratto OpenAPI.

L'obiettivo della tesi è introdurre un Agent Service che permetta di esprimere
una richiesta in linguaggio naturale e di tradurla in una chiamata REST
compatibile con il Persistence Service.

L'agente non sostituisce il Persistence Service e non modifica il suo contratto.

Introduce invece un livello di interpretazione tra la richiesta dell'utente e
le API REST già disponibili nel sistema WLDT.

## Design

### Architectural extension

L'estensione architetturale proposta introduce un nuovo servizio Python tra il
client e il Persistence Service:

```text
Utente / Query Workbench
        ↓
Agent Service
        ↓
Persistence Service
        ↓
MongoDB
```

L'Agent Service utilizza inoltre un modello linguistico locale attraverso
Ollama.

La specifica OpenAPI corrente del Persistence Service viene utilizzata
dinamicamente come contratto per la selezione, la generazione e la validazione
delle chiamate.

L'obiettivo è mantenere separati:

```text
interpretazione del linguaggio naturale
        ↓
controllo deterministico
        ↓
esecuzione REST
```

### Agent Service design

L'implementazione corrente dell'Agent Service si trova in:

```text
05_codice/agent_service
```

La directory:

```text
05_codice/agent
```

rappresenta invece il prototipo storico utilizzato durante le prime fasi
sperimentali.

L'Agent Service corrente è implementato utilizzando FastAPI ed espone i
seguenti endpoint:

```text
GET  /health
GET  /openapi/status
GET  /openapi/operations
POST /query
```

`POST /query` rappresenta il punto di ingresso della pipeline completa di
traduzione NL-to-REST.

### NL-to-REST pipeline

La pipeline corrente è:

```text
richiesta in linguaggio naturale
        ↓
OpenApiLoader
        ↓
OpenApiCatalog
        ↓
ApiSelector
        ↓
top 3 operazioni candidate
        ↓
PromptBuilder
        ↓
Ollama / Qwen3 8B
        ↓
GeneratedApiCall
        ↓
gestione missingInformation
        ↓
ApiCallValidator
        ↓
ApiRequestPreparer
        ↓
RestClient
        ↓
Persistence Service
```

Le responsabilità dei singoli componenti vengono mantenute separate.

Il modello linguistico non è quindi responsabile autonomamente dell'intera
interazione con il backend.

### OpenAPI integration

L'Agent Service recupera dinamicamente la specifica OpenAPI attraverso la
variabile di configurazione:

```text
OPENAPI_SPEC_URL
```

La specifica corrente viene utilizzata per costruire il catalogo delle
operazioni disponibili.

Per ogni operazione vengono conservate informazioni quali:

- metodo HTTP;
- path;
- operationId;
- summary;
- description;
- parametri obbligatori;
- presenza del request body;
- struttura OpenAPI necessaria alle successive fasi.

Questa scelta evita di mantenere manualmente nell'Agent Service un elenco
separato degli endpoint del Persistence Service.

### Candidate selection

Prima dell'utilizzo del modello linguistico viene eseguita una selezione
deterministica delle operazioni.

`ApiSelector` confronta la richiesta naturale con i metadati delle operazioni
OpenAPI e restituisce al massimo tre candidate ordinate per punteggio.

La selezione preliminare è stata introdotta dopo gli esperimenti iniziali, nei
quali i modelli locali mostravano maggiori difficoltà quando ricevevano un
contesto OpenAPI molto ampio.

La pipeline utilizza quindi:

```text
OpenAPI completa
        ↓
selezione deterministica
        ↓
massimo tre candidate
        ↓
LLM
```

invece di delegare direttamente al modello la ricerca all'interno di tutte le
operazioni disponibili.

### Prompt construction

`PromptBuilder` utilizza:

- richiesta dell'utente;
- operazioni candidate;
- informazioni OpenAPI rilevanti.

Il prompt impone al modello di produrre una chiamata appartenente alle
operazioni candidate e di non inventare endpoint o parametri non presenti nel
contratto.

Vengono inoltre incluse regole relative, quando necessarie, a:

- path parameter;
- query parameter;
- struttura del body;
- differenza tra `propertyName` e `propertyId`;
- informazioni mancanti;
- campi obbligatori definiti dalla OpenAPI.

### Structured output

Il modello non restituisce una descrizione testuale libera della chiamata.

Produce invece una struttura `GeneratedApiCall`.

Esempio:

```json
{
  "method": "GET",
  "endpoint": "/hdts/{id}/snapshot",
  "pathParameters": {
    "id": "TEST-001"
  },
  "queryParameters": {},
  "body": null,
  "missingInformation": []
}
```

Il path viene mantenuto nella forma dichiarata dalla OpenAPI.

Nel caso:

```text
/hdts/{id}/snapshot
```

il valore concreto:

```text
TEST-001
```

rimane separato in:

```text
pathParameters.id
```

e viene inserito nell'URL soltanto nella successiva fase di preparazione della
richiesta.

Lo schema dello structured output viene ristretto dinamicamente sulla base
delle operazioni candidate.

Questo permette di applicare alcuni vincoli già nella fase di generazione senza
correggere a posteriori la risposta del modello.

### LLM configuration

La pipeline corrente utilizza:

```text
Ollama
Qwen3 8B
stream = false
think = false
temperature = 0
```

La temperatura zero viene utilizzata per ridurre la variabilità della
generazione.

Questa configurazione non viene considerata una garanzia di determinismo
assoluto.

### Missing information

`GeneratedApiCall` contiene il campo:

```text
missingInformation
```

Il modello deve utilizzarlo quando una chiamata necessita di informazioni che
non possono essere determinate dalla richiesta dell'utente senza inventare
dati.

Se la lista non è vuota, la pipeline interrompe l'esecuzione e restituisce una
risposta HTTP 422.

### Validation before execution

Una chiamata generata dal modello non viene inviata direttamente al Persistence
Service.

`ApiCallValidator` verifica deterministicamente la chiamata rispetto alla
specifica OpenAPI corrente.

I controlli comprendono, quando applicabili:

- combinazione metodo HTTP ed endpoint;
- presenza dei path parameter obbligatori;
- query parameter;
- presenza o assenza del request body;
- tipo radice del body;
- proprietà obbligatorie;
- tipi dei valori;
- enum;
- vincoli specifici di alcune operazioni.

Il validatore non corregge automaticamente la chiamata generata.

Una chiamata non valida viene quindi bloccata e resa osservabile come errore,
invece di essere trasformata silenziosamente in una chiamata differente.

### HTTP request preparation

Dopo la validazione, `ApiRequestPreparer` trasforma `GeneratedApiCall` nella
richiesta HTTP concreta.

Per esempio:

```text
endpoint:
GET /hdts/{id}/snapshot

pathParameters:
id = TEST-001
```

diventa:

```text
GET /hdts/TEST-001/snapshot
```

La richiesta viene quindi eseguita da `RestClient` verso il Persistence Service
configurato.

## Validation

### Preliminary LLM experiments

La fase iniziale del lavoro ha confrontato differenti modelli e differenti
modalità di rappresentazione del contesto OpenAPI.

Sono stati analizzati, tra gli altri:

- ChatGPT;
- Qwen3 4B;
- Qwen3 8B;
- Llama 3.1 8B.

Gli esperimenti preliminari hanno evidenziato che fornire direttamente un
contesto OpenAPI ampio a un modello locale può rendere più difficile la
selezione dell'operazione corretta.

Questa osservazione ha contribuito alla scelta dell'architettura finale basata
su selezione deterministica preliminare e generazione LLM successiva.

### Endpoint-selection experiments

Sono stati inoltre eseguiti esperimenti diagnostici dedicati alla sola
selezione dell'endpoint.

Questi esperimenti hanno permesso di separare il problema:

```text
quale operazione usare?
```

dal problema successivo:

```text
come costruire correttamente la chiamata completa?
```

La selezione preliminare è poi diventata un componente esplicito dell'Agent
Service.

### Automated tests

L'Agent Service dispone di test automatici tramite pytest.

I test vengono utilizzati per verificare i principali componenti della
pipeline, tra cui:

- caricamento della OpenAPI;
- costruzione del catalogo;
- selezione delle candidate;
- costruzione dello structured output;
- validazione;
- preparazione della richiesta;
- gestione degli errori.

### Final controlled pipeline benchmark

Il 10 agosto 2026 è stato congelato un benchmark controllato della pipeline
completa.

Il benchmark utilizza:

```text
5 casi
3 ripetizioni per caso
15 esecuzioni complessive
Qwen3 8B
Ollama
Persistence Service simulato
```

Le metriche aggregate sono:

```text
operation accuracy:      80%
arguments accuracy:      60%
semantic accuracy:       60%
validation pass rate:    80%
execution success rate:  80%
end-to-end success rate: 60%
```

I casi Q2, Q3 e Q5 sono risultati corretti in tutte e tre le ripetizioni.

Q1 ha invece prodotto sistematicamente un'operazione non corretta ed è stato
bloccato dal validatore.

Q4 ha selezionato l'endpoint corretto, ma ha tradotto:

```text
maggiore di
```

utilizzando:

```text
GTE
```

anziché:

```text
GT
```

La chiamata era formalmente valida rispetto alla OpenAPI ed è stata eseguita,
ma non era semanticamente equivalente alla richiesta.

Questo caso evidenzia la distinzione:

```text
validità OpenAPI != correttezza semantica
```

Il benchmark misura quindi separatamente correttezza semantica e validazione
strutturale.

I cinque casi sono stati utilizzati anche durante lo sviluppo e la diagnostica
della pipeline.

Il risultato deve quindi essere interpretato come benchmark controllato e
regressivo e non come stima generale dell'accuratezza dell'agente su richieste
arbitrarie.

Il risultato congelato è:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

Eventuali evoluzioni successive dell'agente non devono modificare
retroattivamente questo risultato.

### Integration with the real WLDT environment

L'11 agosto 2026 è stata avviata la prima verifica dell'Agent Service
nell'ambiente WLDT reale.

Le repository:

```text
whdt-monitor-frontend
hdt-creation-service
persistence-service
whdt-monitor-infra
```

sono state clonate localmente come repository sorelle.

La configurazione development indicata dal progetto WLDT utilizza:

```text
docker-compose.yml
docker-compose.dev.yml
```

e costruisce frontend, Creation Service e Persistence Service direttamente dai
repository locali.

### Windows development environment

Per eseguire lo stack è stato configurato Docker Desktop con backend WSL 2.

Durante la prima build dei due servizi Kotlin è stato individuato un problema
relativo alle terminazioni di riga di:

```text
gradlew
```

Il repository Git conteneva lo script con terminazioni LF, mentre il checkout
Windows lo aveva convertito in CRLF.

All'interno del container Linux questo impediva l'esecuzione di:

```text
./gradlew
```

La configurazione Git locale dei repository interessati è stata quindi
impostata in modo da preservare le terminazioni LF.

Dopo questa correzione lo stack development è stato costruito e avviato
correttamente.

### Real OpenAPI loading

L'Agent Service è stato inizialmente mantenuto sul sistema host, mentre i
servizi WLDT sono stati eseguiti tramite Docker.

Questa scelta consente di verificare prima la comunicazione applicativa con il
Persistence Service e di affrontare in un secondo momento la containerizzazione
dell'agente.

L'Agent Service è stato configurato per recuperare la specifica da:

```text
http://127.0.0.1:8081/openapi.yaml
```

La verifica di:

```text
GET /openapi/status
```

ha restituito:

```text
status = ok
OpenAPI version = 3.1.1
path count = 26
```

La verifica di:

```text
GET /openapi/operations
```

ha prodotto un catalogo di:

```text
37 operazioni
```

Sono risultati operativi anche:

```text
GET /health
GET /openapi/status
GET /openapi/operations
```

### First real end-to-end smoke test

La prima richiesta utilizzata per verificare la pipeline sul Persistence
Service reale è stata:

```text
Mostrami i nomi distinti delle proprietà disponibili.
```

L'Agent Service ha generato:

```text
GET /properties/names
```

La chiamata ha superato la validazione deterministica.

`ApiRequestPreparer` ha costruito:

```text
GET http://127.0.0.1:8081/properties/names
```

Il Persistence Service reale ha restituito HTTP 200.

In quel momento il database non conteneva ancora HDT, quindi il body della
risposta era un array vuoto.

Il test ha comunque verificato per la prima volta la sequenza:

```text
linguaggio naturale
→ Agent Service
→ OpenAPI reale
→ LLM
→ validazione
→ richiesta REST
→ Persistence Service reale
```

### Real HDT creation

Per eseguire una verifica su dati reali è stato successivamente utilizzato il
flusso JSON del frontend e dell'HDT Creation Service.

L'importazione JSON del frontend invia gli oggetti a:

```text
POST /api/hdts/json/batch
```

Il Creation Service richiede per ogni elemento JSON almeno i campi:

```text
ID
Age
task
Sex
```

ed utilizza gli altri valori primitivi come proprietà del Digital Twin.

È stato creato il seguente HDT di test:

```text
TEST-001
```

con:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

Il Digital Twin è stato correttamente memorizzato nel Persistence Service.

La richiesta:

```text
GET /hdts
```

ha successivamente restituito `TEST-001`.

### Direct snapshot verification

Prima di coinvolgere l'Agent Service è stato verificato direttamente
l'endpoint:

```text
GET /hdts/TEST-001/snapshot
```

Il Persistence Service ha restituito HTTP 200.

La risposta conteneva:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

I valori risultavano provenienti dalle osservazioni create durante
l'importazione JSON.

### Parameterized NL-to-REST verification

Dopo la verifica diretta è stata inviata all'Agent Service la richiesta:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

Il selettore ha classificato come prima candidata:

```text
GET /hdts/{id}/snapshot
```

Il modello ha generato:

```json
{
  "method": "GET",
  "endpoint": "/hdts/{id}/snapshot",
  "pathParameters": {
    "id": "TEST-001"
  },
  "queryParameters": {},
  "body": null,
  "missingInformation": []
}
```

La chiamata ha superato la validazione:

```text
valid = true
```

`ApiRequestPreparer` ha costruito:

```text
GET http://127.0.0.1:8081/hdts/TEST-001/snapshot
```

Il Persistence Service reale ha restituito:

```text
HTTP 200
```

e l'Agent Service ha restituito i valori reali:

```text
Age = 30
task = rest
Sex = M
heartRate = 72
systolicPressure = 120
```

È stata quindi verificata con successo la pipeline:

```text
linguaggio naturale
→ Agent Service
→ OpenAPI reale
→ selezione candidate
→ Qwen3 8B
→ GeneratedApiCall
→ validazione OpenAPI
→ preparazione HTTP
→ Persistence Service reale
→ MongoDB
→ risposta reale
```

Questo test è distinto dal benchmark quantitativo del 10 agosto.

Il benchmark del 10 agosto utilizza un Persistence Service simulato e rimane
congelato.

La verifica dell'11 agosto rappresenta invece uno smoke test di integrazione
con il backend WLDT reale e non viene utilizzata per modificare retroattivamente
le metriche del benchmark.

### Observed Persistence Service behavior

Durante la verifica è stato osservato un comportamento differente tra due
endpoint.

La richiesta:

```text
GET /hdts/TEST-001
```

ha restituito HTTP 500 con il messaggio:

```text
state should be: hexString has 24 characters
```

La richiesta:

```text
GET /hdts/TEST-001/snapshot
```

ha invece restituito correttamente HTTP 200.

Il comportamento viene registrato come osservazione relativa al Persistence
Service.

Non viene introdotto nell'Agent Service alcun workaround per modificare
automaticamente l'identificatore o compensare il comportamento del backend.

### Current limitations

La prima integrazione reale verifica l'Agent Service eseguito sull'host e il
Persistence Service eseguito nello stack Docker.

Rimangono da completare:

- containerizzazione dell'Agent Service;
- inserimento dell'Agent Service nel `docker-compose.dev`;
- comunicazione container-to-container con il Persistence Service;
- comunicazione tra il container dell'agente e Ollama;
- integrazione della modalità Natural Language nel Query Workbench;
- valutazione su un insieme di richieste indipendente dai casi utilizzati
  durante lo sviluppo;
- eventuale evoluzione della metodologia di valutazione sulla base dei
  successivi feedback del relatore.