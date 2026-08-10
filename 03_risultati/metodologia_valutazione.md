# Metodologia di valutazione

La valutazione del lavoro è stata articolata in due fasi distinte: una fase
sperimentale iniziale, finalizzata al confronto tra modelli e modalità di
costruzione del contesto, e una fase finale dedicata alla valutazione della
pipeline completa dell'Agent Service.

Le due fasi utilizzano metriche differenti e non devono essere confrontate
come se rappresentassero lo stesso esperimento.

## Benchmark sperimentali sui modelli

Gli esperimenti E002, E003, E004, E005, E006 ed E009 utilizzano cinque
richieste e vengono valutati su 50 punti. Per ogni richiesta sono assegnati da
0 a 2 punti a ciascuna delle seguenti voci:

1. metodo HTTP;
2. endpoint;
3. struttura dell'input;
4. fedeltà alla specifica OpenAPI;
5. gestione delle informazioni mancanti.

Il punteggio valuta la risposta prodotta in una singola esecuzione. Non misura
la variabilità tra esecuzioni dello stesso modello.

Questi benchmark sono stati utilizzati in modo esplorativo per osservare il
comportamento dei modelli in configurazioni differenti e per motivare le
successive scelte progettuali, in particolare la selezione preliminare di un
insieme ristretto di operazioni candidate prima della generazione LLM.

## Esperimenti diagnostici

E007 ed E008 misurano soltanto la selezione dell'endpoint:

- E007: un caso su un solo endpoint, punteggio 10/10;
- E008: cinque casi su cinque descrizioni sintetiche, accuratezza 5/5.

Questi risultati non sono confrontabili direttamente con i punteggi su 50 dei
benchmark completi.

## Distinzione tra contratto e implementazione

Il prompt dei benchmark sperimentali imponeva di utilizzare esclusivamente
l'OpenAPI. Le valutazioni storiche devono quindi essere interpretate rispetto
al contratto disponibile al momento dell'esecuzione.

L'analisi successiva del codice del Persistence Service ha evidenziato che
`POST /query/event/values/history` usa soltanto `hdtId` e `propertyName`,
ignorando `from` e `to`. Per l'interrogazione dei valori di una proprietà in un
intervallo viene invece utilizzato
`POST /query/event/values/valuesByName`.

Per `POST /query/event/stats`, gli array `hdtIds`, `modelIds` e `modelNames`
devono essere presenti nel body. Nella configurazione considerata, gli array
vuoti rappresentano l'assenza del relativo filtro.

Queste differenze non rendono inutili gli esperimenti precedenti, ma impediscono
di usare senza revisione la loro ground truth come specifica dell'integrazione
finale.

## Benchmark controllato della pipeline finale

La pipeline completa è stata valutata con un benchmark separato, memorizzato in
`02_esperimenti/pipeline_finale`.

Il benchmark comprende cinque richieste rappresentative di funzionalità
differenti:

1. elenco dei Digital Twin;
2. snapshot corrente di un Digital Twin;
3. valori di una proprietà in un intervallo temporale;
4. confronto sul valore di una proprietà;
5. statistiche aggregate senza filtri su HDT o modello.

Ogni caso viene ripetuto tre volte, per un totale di 15 esecuzioni. Le tre
ripetizioni hanno lo scopo di osservare la stabilità del comportamento sui casi
selezionati e non rappresentano 15 richieste semanticamente indipendenti.

### Configurazione

Il benchmark valuta la pipeline completa:

`richiesta NL -> caricamento OpenAPI -> catalogo -> selezione candidati -> prompt ristretto -> LLM -> validazione OpenAPI -> preparazione HTTP -> Persistence Service simulato`.

La generazione è eseguita localmente con Qwen3 8B tramite Ollama. Il
Persistence Service reale non viene utilizzato nel benchmark finale: un mock
espone la specifica OpenAPI e gli endpoint necessari per verificare che la
richiesta preparata raggiunga effettivamente il livello di esecuzione.

### Ground truth

Il file `cases.json` definisce per ogni richiesta una ground truth completa,
comprendente:

- metodo HTTP;
- endpoint OpenAPI;
- path parameters;
- query parameters;
- body;
- `missingInformation`.

La valutazione semantica confronta quindi l'intera chiamata generata con la
chiamata attesa, e non soltanto metodo ed endpoint.

### Metriche

Il runner distingue i seguenti livelli:

- **operation_correct**: metodo HTTP ed endpoint coincidono con la ground truth;
- **arguments_correct**: path parameters, query parameters, body e
  `missingInformation` coincidono con la ground truth;
- **semantic_correct**: sia l'operazione sia gli argomenti sono corretti;
- **validation_valid**: il validatore OpenAPI viene raggiunto e accetta la
  chiamata generata;
- **execution_success**: la richiesta raggiunge il Persistence Service simulato
  e riceve una risposta HTTP 2xx;
- **end_to_end_success**: correttezza semantica, validazione ed esecuzione sono
  tutte soddisfatte.

La separazione tra `semantic_correct` e `validation_valid` è intenzionale. Una
chiamata può infatti rispettare formalmente il contratto OpenAPI ma tradurre in
modo non equivalente l'intenzione espressa dall'utente.

### Tempi

Per ogni esecuzione viene misurato il tempo wall-clock complessivo della
richiesta a `POST /query`. Quando disponibili, vengono inoltre conservate le
metriche restituite da Ollama, tra cui durata totale, token di prompt valutati e
token generati.

## Risultato congelato della pipeline

Il benchmark finale congelato è contenuto nel file
`results_20260810_201100.json` e comprende 15 esecuzioni. I risultati aggregati
sono documentati separatamente in
`03_risultati/benchmark_pipeline_finale.md`.

Il file dei risultati e la configurazione associata devono essere conservati
senza modifiche retroattive. Eventuali evoluzioni successive dell'agente devono
essere valutate in un nuovo esperimento, mantenendo separati i risultati.

## Limiti metodologici

### Benchmark sperimentali iniziali

- una sola esecuzione per configurazione;
- tempi non raccolti in modo uniforme per tutti i modelli;
- confronto tra un servizio cloud e modelli locali non controllato sul piano
  hardware e della versione esatta del modello;
- benchmark ristretto a cinque richieste;
- punteggi assegnati manualmente sulla base della rubrica definita sopra.

### Benchmark della pipeline finale

- il benchmark contiene soltanto cinque casi funzionali;
- le tre ripetizioni misurano soprattutto la stabilità dei casi scelti;
- i cinque casi sono stati utilizzati anche durante lo sviluppo e la diagnostica
  della pipeline e non costituiscono quindi un test set completamente
  indipendente;
- lo scoring semantico utilizza una ground truth esatta e controllata;
- il Persistence Service utilizzato per l'esecuzione è simulato;
- il benchmark verifica il comportamento dell'Agent Service fino alla chiamata
  REST, ma non valuta il comportamento del database o del Persistence Service
  reale su dati di produzione.

I risultati devono quindi essere interpretati come valutazione controllata e
regressiva della pipeline nella configurazione considerata, non come stima
generale dell'accuratezza dell'agente su richieste arbitrarie.