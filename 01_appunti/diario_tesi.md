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