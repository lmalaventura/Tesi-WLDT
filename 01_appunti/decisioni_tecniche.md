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

## Strategia di integrazione incrementale con WLDT reale — 11/08/2026

### Contesto

Il sistema finale dovrà integrare l'Agent Service Python con i servizi WLDT
eseguiti tramite Docker.

L'introduzione contemporanea della nuova pipeline applicativa e del networking
Docker avrebbe però reso più difficile distinguere problemi appartenenti a
livelli differenti.

### Decisione

Procedere in due fasi.

Prima fase:

```text
Agent Service eseguito sull'host
        ↓
Persistence Service eseguito in Docker
```

Seconda fase:

```text
Agent Service eseguito in Docker
        ↓
Persistence Service eseguito in Docker
```

### Motivazione

La prima configurazione permette di verificare isolatamente:

- caricamento della OpenAPI reale;
- selezione delle operazioni;
- generazione LLM;
- validazione;
- preparazione della richiesta;
- comunicazione REST con il backend reale.

Soltanto dopo aver verificato questi aspetti viene introdotta la
containerizzazione dell'Agent Service.

In questo modo eventuali errori successivi potranno essere attribuiti con
maggiore precisione alla configurazione Docker o al networking.

### Esito

La prima fase è stata verificata con successo.

L'Agent Service sull'host è riuscito a:

```text
recuperare la OpenAPI reale
→ costruire il catalogo
→ selezionare le candidate
→ generare la chiamata
→ validarla
→ prepararla
→ eseguirla sul Persistence Service reale
→ ricevere dati memorizzati in MongoDB
```

La containerizzazione dell'Agent Service viene quindi rimandata alla fase
successiva.

---

## Utilizzo della OpenAPI reale come contratto runtime — 11/08/2026

### Decisione

Durante l'integrazione utilizzare direttamente:

```text
http://127.0.0.1:8081/openapi.yaml
```

come sorgente della specifica dell'Agent Service.

### Motivazione

La pipeline deve operare sul contratto effettivamente esposto dal Persistence
Service in esecuzione.

Il catalogo delle operazioni non deve dipendere da una copia manualmente
sincronizzata della specifica durante il funzionamento normale dell'agente.

### Esito

La OpenAPI reale caricata durante il test risulta:

```text
OpenAPI 3.1.1
26 path
37 operazioni
```

L'Agent Service ha costruito correttamente il proprio catalogo a partire da tale
specifica.

---

## Selezione preliminare prima del modello — conferma su backend reale — 11/08/2026

### Osservazione

Nel test parametrizzato:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

`ApiSelector` ha classificato al primo posto:

```text
GET /hdts/{id}/snapshot
```

seguito da operazioni semanticamente vicine.

### Decisione

Mantenere l'architettura:

```text
OpenAPI
→ selezione deterministica top-k
→ LLM
```

invece di fornire indiscriminatamente al modello tutte le operazioni.

### Motivazione

La selezione preliminare riduce il contesto fornito al modello e separa il
problema del retrieval delle operazioni dal problema della costruzione della
chiamata.

Il test sul backend reale conferma che tale struttura può portare
correttamente l'operazione desiderata nel contesto del modello.

---

## Separazione tra benchmark quantitativo e smoke test reale — 11/08/2026

### Decisione

Mantenere separati:

```text
benchmark controllato del 10/08/2026
```

e:

```text
smoke test sul WLDT reale dell'11/08/2026
```

### Motivazione

Il benchmark del 10 agosto utilizza:

```text
5 casi
3 ripetizioni
15 run
Persistence Service simulato
```

e misura quantitativamente il comportamento della pipeline su uno scenario
controllato.

I casi sono stati utilizzati anche durante lo sviluppo e la diagnostica.

Il risultato deve quindi essere interpretato come benchmark regressivo e non
come valutazione indipendente della capacità generale dell'agente.

Lo smoke test dell'11 agosto ha invece un obiettivo differente:

```text
verificare che la pipeline funzioni contro il backend WLDT reale
```

e non produrre nuove metriche di accuratezza.

### Conseguenza

L'esito positivo dell'integrazione reale non modifica retroattivamente:

```text
operation accuracy
arguments accuracy
semantic accuracy
validation pass rate
execution success rate
end-to-end success rate
```

del benchmark congelato.

Eventuali benchmark futuri dovranno essere versionati separatamente.

---

## Creazione dei dati di integrazione tramite HDT Creation Service — 11/08/2026

### Problema

Il database iniziale dell'ambiente development era vuoto.

Per verificare gli endpoint parametrizzati dell'agente era quindi necessario
creare almeno un HDT.

### Decisione

Non inserire direttamente documenti nel Persistence Service o in MongoDB.

Utilizzare invece il normale flusso:

```text
frontend
→ HDT Creation Service
→ Persistence Service
→ MongoDB
```

### Motivazione

In questo modo i dati di test vengono creati utilizzando le stesse trasformazioni
e convenzioni previste dal sistema WLDT.

Il test dell'agente opera quindi su dati generati attraverso un flusso
applicativo reale e non su documenti costruiti manualmente esclusivamente per
far passare il test.

### Implementazione

È stato utilizzato l'input JSON:

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

Il Creation Service ha trasformato i valori nei relativi oggetti di dominio e
ha creato anche le osservazioni iniziali.

---

## Gestione dei line ending Gradle su Windows — 11/08/2026

### Problema

La prima build Docker dei servizi Kotlin falliva durante:

```text
./gradlew buildFatJar --no-daemon
```

nonostante `gradlew` fosse presente nel build context.

Il controllo Git mostrava:

```text
i/lf w/crlf
```

Il repository conteneva quindi il file con terminazioni LF, mentre il working
tree Windows lo aveva convertito in CRLF.

### Decisione

Configurare localmente Git nei repository interessati in modo da preservare LF
e ripristinare `gradlew` dalla versione archiviata.

### Alternative non adottate

Non modificare i Dockerfile ufficiali aggiungendo operazioni quali:

```text
dos2unix gradlew
```

o trasformazioni equivalenti.

### Motivazione

Il problema non appartiene al Dockerfile del progetto.

Il file corretto è già presente nel repository e deve semplicemente essere
mantenuto correttamente nel checkout locale.

La soluzione evita inoltre modifiche non necessarie alle repository WLDT.

---

## Nessun workaround dell'Agent Service per GET /hdts/{id} — 11/08/2026

### Osservazione

Dopo la creazione dell'HDT:

```text
TEST-001
```

la richiesta:

```text
GET /hdts
```

lo elenca correttamente.

La richiesta:

```text
GET /hdts/TEST-001
```

restituisce invece:

```text
HTTP 500
state should be: hexString has 24 characters
```

La richiesta:

```text
GET /hdts/TEST-001/snapshot
```

con lo stesso identificatore restituisce correttamente:

```text
HTTP 200
```

### Decisione

Non modificare l'Agent Service per:

- trasformare artificialmente `TEST-001`;
- sostituire l'identificatore con un valore MongoDB;
- intercettare questa specifica operazione e riscriverla;
- nascondere l'errore del Persistence Service.

### Motivazione

L'Agent Service deve generare e validare le chiamate rispetto al contratto
OpenAPI.

Un comportamento anomalo di uno specifico endpoint del backend deve essere
analizzato al livello appropriato e non compensato introducendo logica
speciale nell'agente.

### Conseguenza

Il comportamento viene registrato come osservazione tecnica separata.

L'eventuale analisi dell'implementazione di `GET /hdts/{id}` potrà essere
effettuata successivamente senza alterare la pipeline NL-to-REST.

---

## Conservazione dei dati Docker durante lo sviluppo — 11/08/2026

### Decisione

Per arrestare l'ambiente development utilizzare:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

senza:

```text
-v
```

### Motivazione

Il comando `down` arresta e rimuove i container mantenendo il volume MongoDB.

Il comando:

```text
down -v
```

rimuoverebbe invece anche i volumi e cancellerebbe i dati utilizzati durante i
test.

### Conseguenza

`TEST-001` e gli altri eventuali dati di integrazione possono essere
riutilizzati nelle sessioni successive senza dover ricostruire ogni volta il
dataset locale.

---

## Prossimo livello di integrazione — 11/08/2026

### Decisione

Dopo il successo della configurazione host-to-container, il prossimo intervento
sull'architettura sarà la containerizzazione di:

```text
05_codice/agent_service
```

e il suo inserimento nello stack development WLDT.

### Configurazione prevista

All'interno della rete Docker il Persistence Service dovrà essere raggiunto
tramite il nome del servizio:

```text
http://persistence-service:8081
```

anziché tramite:

```text
http://127.0.0.1:8081
```

L'accesso a Ollama, che rimane inizialmente sull'host Windows, dovrà invece
essere configurato utilizzando il meccanismo appropriato per la comunicazione
container-to-host.

### Criterio di verifica

La containerizzazione verrà considerata corretta quando sarà possibile ripetere
lo stesso test già riuscito:

```text
richiesta naturale
→ Agent Service
→ GET /hdts/{id}/snapshot
→ Persistence Service
→ HTTP 200
```

con Agent Service e Persistence Service integrati nello stack Docker
development.

---

## Containerizzazione dell'Agent Service — 12/08/2026

### Problema

L'Agent Service era stato verificato contro il Persistence Service reale, ma
veniva ancora eseguito direttamente sull'host Windows.

La configurazione finale richiede invece che il servizio possa essere integrato
nell'ambiente Docker development di WLDT.

### Decisione

Containerizzare:

```text
05_codice/agent_service
```

utilizzando un'immagine Python 3.12 e le dipendenze già definite in:

```text
pyproject.toml
uv.lock
```

### Implementazione

Sono stati aggiunti:

```text
Dockerfile
.dockerignore
```

Il container avvia:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

ed espone la porta:

```text
8000
```

### Motivazione

La containerizzazione rende l'Agent Service coerente con l'architettura
distribuita degli altri servizi WLDT e permette di verificare il servizio nello
stesso ambiente di rete del Persistence Service.

---

## Verifica standalone prima dell'integrazione Compose — 12/08/2026

### Decisione

Prima di inserire l'Agent Service nello stack development, eseguire una verifica
standalone del container.

### Configurazione

Utilizzare:

```text
OLLAMA_BASE_URL=http://host.docker.internal:11434
PERSISTENCE_SERVICE_BASE_URL=http://host.docker.internal:8081
OPENAPI_SPEC_URL=http://host.docker.internal:8081/openapi.yaml
```

### Motivazione

La verifica separata consente di distinguere:

```text
problemi del Dockerfile/container
```

da:

```text
problemi del networking Compose
```

La stessa strategia incrementale era stata utilizzata il giorno precedente per
distinguere problemi della pipeline da problemi di containerizzazione.

### Esito

Il container standalone ha:

- avviato correttamente FastAPI/Uvicorn;
- raggiunto la OpenAPI reale;
- raggiunto Ollama sull'host;
- eseguito Qwen3 8B;
- generato e validato la chiamata;
- raggiunto il Persistence Service;
- restituito lo snapshot reale di `TEST-001`.

---

## Comunicazione con Ollama dal container — 12/08/2026

### Problema

Ollama e Qwen3 8B rimangono in esecuzione direttamente sull'host Windows.

All'interno del container:

```text
localhost
```

identifica il container stesso e non l'host.

### Decisione

Configurare:

```text
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Motivazione

L'Agent Service deve raggiungere il runtime Ollama eseguito sull'host senza
containerizzare contemporaneamente anche il modello.

### Esito

La configurazione è stata verificata attraverso un'esecuzione completa di
`POST /query`.

Non è stato necessario modificare `OllamaClient` o la logica applicativa.

---

## Comunicazione Docker-to-Docker con Persistence Service — 12/08/2026

### Problema

Durante il test standalone il Persistence Service veniva raggiunto tramite:

```text
http://host.docker.internal:8081
```

Una volta inseriti Agent Service e Persistence Service nello stesso progetto
Compose, il passaggio attraverso l'host non è necessario.

### Decisione

Utilizzare:

```text
PERSISTENCE_SERVICE_BASE_URL=http://persistence-service:8081
```

e:

```text
OPENAPI_SPEC_URL=http://persistence-service:8081/openapi.yaml
```

### Motivazione

L'Agent Service deve utilizzare la rete interna dello stack e individuare il
Persistence Service tramite il nome del servizio Compose.

Questa configurazione riduce la dipendenza dalle porte pubblicate sull'host per
la comunicazione tra componenti interni.

### Esito

`GET /openapi/status` ha restituito:

```text
source = http://persistence-service:8081/openapi.yaml
```

confermando che il contratto OpenAPI viene recuperato tramite la comunicazione
Docker-to-Docker.

---

## Inserimento dell'Agent Service nello stack development — 12/08/2026

### Decisione

Estendere la configurazione development con:

```text
agent-service
```

senza modificare la configurazione applicativa Python.

### Configurazione

Il servizio utilizza:

```text
build context = ../../Tesi-WLDT/05_codice/agent_service
port = 8000:8000
```

e dipende dal:

```text
persistence-service
```

### Motivazione

L'Agent Service rimane un microservizio separato, coerentemente con
l'architettura definita per la tesi.

La configurazione tramite variabili d'ambiente permette allo stesso codice di
essere eseguito:

```text
localmente
```

oppure:

```text
dentro Docker
```

senza introdurre branch applicativi specifici per l'ambiente.

---

## Criterio di successo della containerizzazione raggiunto — 12/08/2026

### Criterio precedente

L'11 agosto era stato stabilito che la seconda fase sarebbe stata considerata
completata quando fosse stato possibile eseguire:

```text
richiesta naturale
→ Agent Service in Docker
→ GET /hdts/{id}/snapshot
→ Persistence Service in Docker
→ HTTP 200
```

### Verifica

La richiesta:

```text
Mostrami il valore corrente delle proprieta del Digital Twin con id "TEST-001".
```

ha prodotto:

```text
method = GET
endpoint = /hdts/{id}/snapshot
pathParameters.id = TEST-001
```

La validazione ha restituito:

```text
valid = true
```

e la richiesta preparata è stata:

```text
GET http://persistence-service:8081/hdts/TEST-001/snapshot
```

Il Persistence Service ha restituito:

```text
HTTP 200
```

con i valori reali del Digital Twin.

### Decisione

Considerare completata la seconda fase della strategia di integrazione
incrementale.

La configurazione verificata è:

```text
Agent Service in Docker
        ↓
Persistence Service in Docker
        ↓
MongoDB
```

con:

```text
Agent Service in Docker
        ↓
Ollama sull'host
```

per la componente LLM.

---

## Nessuna modifica del benchmark dopo la containerizzazione — 12/08/2026

### Decisione

Non ripetere o modificare il benchmark congelato del 10 agosto come conseguenza
della containerizzazione.

### Motivazione

Le modifiche del 12 agosto riguardano:

```text
packaging
containerizzazione
networking
integrazione infrastrutturale
```

e non costituiscono un intervento finalizzato a correggere i casi Q1 o Q4.

Il benchmark precedente rimane quindi il checkpoint quantitativo della pipeline
al momento del congelamento.

Le verifiche Docker vengono mantenute come test di integrazione separati.

---

## Prossimo livello di integrazione — frontend — 12/08/2026

### Decisione

Dopo il completamento della containerizzazione, il prossimo intervento
funzionale riguarda l'integrazione dell'Agent Service nel Query Workbench.

### Obiettivo

Passare dalla verifica:

```text
PowerShell
→ Agent Service
→ Persistence Service
```

alla verifica:

```text
browser
→ Query Workbench
→ Agent Service
→ Persistence Service
→ risultato visualizzato nel frontend
```

### Vincolo

L'integrazione frontend non deve bypassare:

```text
POST /query
```

né duplicare nel frontend la logica di:

```text
selezione
generazione
validazione
preparazione REST
```

Queste responsabilità rimangono appartenenti all'Agent Service.

---

## Integrazione dell'Agent Service nel Query Workbench — 12/08/2026

### Decisione

Integrare l'Agent Service come nuova modalità del Query Workbench esistente,
senza creare una pagina frontend separata.

### Implementazione

È stata aggiunta la scheda:

```text
Natural Language
```

e il componente:

```text
NaturalLanguageQueryPanel
```

### Motivazione

Il Query Workbench rappresenta già il punto dell'interfaccia dedicato
all'interrogazione dei dati.

La modalità naturale costituisce quindi una modalità alternativa di costruzione
della stessa operazione logica, mantenendo coerente l'organizzazione
dell'interfaccia.

---

## Nessuna chiamata diretta browser-to-Agent — 12/08/2026

### Decisione

Non configurare il browser per chiamare direttamente:

```text
http://localhost:8000
```

### Motivazione

Il browser non deve dipendere direttamente dalla topologia interna dello stack
Docker.

Il frontend Next.js funge da livello server-side tra browser e Agent Service.

La catena scelta è:

```text
Browser
→ Next.js
→ Agent Service
```

invece di:

```text
Browser
→ Agent Service
```

---

## Sostituzione della rewrite con Route Handler esplicita — 12/08/2026

### Problema

La prima integrazione utilizzava una rewrite Next.js:

```text
/api/agent/:path*
→
http://agent-service:8000/:path*
```

Durante una richiesta completa il proxy ha prodotto:

```text
ECONNRESET
socket hang up
```

### Evidenza diagnostica

La comunicazione diretta:

```text
frontend container
→ Agent Service container
```

è stata verificata separatamente con successo.

Sia:

```text
GET /health
```

sia:

```text
POST /query
```

hanno restituito HTTP 200.

### Decisione

Sostituire la rewrite con:

```text
src/app/api/agent/query/route.ts
```

che utilizza una richiesta `fetch` server-side esplicita.

### Motivazione

La Route Handler rende controllabile il comportamento della richiesta
Agent-specifica e permette di propagare esplicitamente:

- body;
- content type;
- status code;
- risposta del servizio;
- errore di collegamento.

Le rewrite esistenti per Creation Service e Persistence Service rimangono
inalterate.

---

## Configurazione runtime dell'Agent nel frontend — 12/08/2026

### Decisione

Fornire al container frontend:

```text
AGENT_SERVICE_URL=http://agent-service:8000
```

come variabile d'ambiente runtime.

### Motivazione

La Route Handler viene eseguita server-side all'interno del container Next.js e
deve raggiungere l'Agent Service attraverso il DNS della rete Compose.

Non è necessario inserire l'indirizzo dell'Agent Service nel codice client
eseguito nel browser.

---

## Criterio finale di completamento dell'implementazione — 12/08/2026

### Criterio

Considerare completato lo scope funzionale principale quando sia verificabile:

```text
Browser
→ Query Workbench
→ richiesta naturale
→ Agent Service
→ Persistence Service
→ MongoDB
→ risultato visualizzato
```

### Esito

Il criterio è stato soddisfatto utilizzando:

```text
TEST-001
```

La richiesta naturale ha prodotto:

```text
GET /hdts/{id}/snapshot
```

la validazione è risultata corretta e il Persistence Service ha restituito HTTP
200.

I dati reali sono stati visualizzati nel Query Workbench.

### Decisione

Congelare l'implementazione funzionale al checkpoint del:

```text
12/08/2026
```

salvo:

- bug successivamente individuati;
- richieste del relatore;
- attività necessarie alla valutazione finale;
- rifiniture non bloccanti.