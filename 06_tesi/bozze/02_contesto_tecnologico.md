# Contesto tecnologico — bozza

## API REST e specifica OpenAPI

Nel sistema WLDT i diversi componenti comunicano attraverso interfacce HTTP e, in particolare, il Persistence Service espone tramite API REST le funzionalità necessarie per memorizzare e interrogare i dati. Ogni operazione è identificata da un metodo HTTP e da un percorso e può richiedere anche path parameter, query parameter o un request body.
Per il lavoro svolto nella tesi non è sufficiente che la chiamata prodotta dall'agente sia solamente leggibile dal programma, ma deve anche corrispondere a una delle operazioni realmente disponibili nel Persistence Service. La specifica OpenAPI assume quindi un ruolo centrale, perché descrive il contratto attraverso cui vengono definiti gli endpoint, i parametri richiesti e le strutture dei dati accettate dal servizio.
L'Agent Service non mantiene una lista indipendente degli endpoint. La specifica viene recuperata dinamicamente dall'indirizzo configurato e le operazioni contenute al suo interno vengono trasformate in un catalogo normalizzato, nel quale sono mantenute le informazioni utili alle fasi successive della pipeline. Questo catalogo viene utilizzato sia per individuare le operazioni più compatibili con la richiesta dell'utente, sia per mantenere un collegamento con la definizione OpenAPI necessaria alla successiva validazione.

## Large Language Model e inferenza locale

Il Large Language Model viene utilizzato per interpretare la richiesta espressa dall'utente e trasformarla in una rappresentazione strutturata della chiamata REST proposta. Il modello non viene però utilizzato come componente autonomo a cui affidare direttamente l'interazione con il backend.
Prima dell'inferenza, l'Agent Service effettua una selezione deterministica delle operazioni e costruisce un prompt contenente soltanto un insieme ristretto di candidate. Questa scelta deriva anche dai risultati degli esperimenti preliminari, nei quali l'utilizzo dell'intera specifica OpenAPI come contesto non aveva mostrato un vantaggio costante, soprattutto con i modelli locali di dimensioni più ridotte.
Nell'implementazione corrente viene utilizzato Qwen3 8B tramite Ollama. L'inferenza avviene localmente, permettendo di mantenere sotto controllo l'ambiente utilizzato durante lo sviluppo e la sperimentazione senza dipendere dall'invocazione di un servizio LLM remoto.
Al modello viene richiesto un oggetto JSON compatibile con la struttura `GeneratedApiCall`, contenente metodo HTTP, endpoint, path parameter, query parameter, eventuale request body e informazioni mancanti. L'utilizzo di un output strutturato facilita l'elaborazione della risposta, ma non garantisce autonomamente che la chiamata prodotta sia conforme alla specifica OpenAPI. Per questo motivo la generazione viene sempre seguita da una fase di validazione deterministica.

## Agent Service, FastAPI e comunicazione HTTP

La logica relativa all'interpretazione in linguaggio naturale è stata isolata in un servizio dedicato, denominato Agent Service. In questo modo il nuovo componente si adatta alle interfacce già offerte dal Persistence Service senza introdurre la logica LLM direttamente nel backend esistente.
L'Agent Service è implementato in Python utilizzando FastAPI. L'endpoint principale `POST /query` riceve il testo dell'utente e coordina le varie fasi della pipeline, dalla lettura della specifica OpenAPI fino all'eventuale esecuzione della chiamata REST. Sono inoltre presenti endpoint diagnostici utilizzati per verificare lo stato del servizio e il caricamento delle operazioni disponibili.
Pydantic viene utilizzato per definire e verificare le principali strutture di input e output, mentre `httpx` gestisce le comunicazioni HTTP verso Ollama, la risorsa OpenAPI e il Persistence Service. La separazione tra i diversi componenti permette di mantenere distinte la generazione del modello, la validazione della chiamata e la sua effettiva esecuzione.

## Containerizzazione e integrazione con WLDT

Una volta completata la pipeline, l'Agent Service è stato containerizzato e inserito nello stack Docker utilizzato per lo sviluppo di WLDT. All'interno della rete Docker il servizio comunica direttamente con il Persistence Service tramite il relativo nome di servizio, mentre Ollama e Qwen3 8B rimangono in esecuzione sull'host di sviluppo.
L'integrazione è stata completata anche nel frontend aggiungendo al Query Workbench una modalità dedicata alle richieste in linguaggio naturale. Il browser comunica con una Route Handler di Next.js, che inoltra la richiesta all'Agent Service dalla parte server senza esporre direttamente al client l'indirizzo interno del container.
Questa configurazione ha permesso di verificare l'Agent Service non soltanto come componente isolato, ma all'interno del flusso completo del sistema WLDT, dalla richiesta inserita nel frontend fino all'esecuzione sul Persistence Service e alla visualizzazione del risultato.