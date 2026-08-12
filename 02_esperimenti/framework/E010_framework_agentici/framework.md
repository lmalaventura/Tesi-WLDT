# E010 — Studio degli approcci per l'orchestrazione LLM

## Obiettivo

Confrontare LangChain, smolagents e una pipeline sviluppata nel progetto per
stabilire quale approccio sia più adatto al caso d'uso WLDT.
E010 è uno studio documentale e progettuale. Non misura tempi, accuratezza o
consumo di risorse dei tre approcci e non deve essere presentato come un
benchmark prestazionale.

## Requisiti del caso d'uso

Il componente da realizzare deve:

1. ricevere una richiesta in linguaggio naturale;
2. utilizzare la specifica OpenAPI aggiornata del Persistence Service;
3. selezionare un insieme controllato di operazioni candidate;
4. generare metodo, path e parametri della richiesta;
5. produrre un output JSON strutturato;
6. validare la chiamata rispetto alla stessa OpenAPI;
7. eseguire la richiesta sul Persistence Service;
8. inoltrare il risultato al client.

Il flusso previsto è deterministico. Nella prima versione non sono richiesti
memoria conversazionale, pianificazione autonoma, scelta dinamica di strumenti
eterogenei o cicli agentici multi-step.

## LangChain

LangChain mette a disposizione astrazioni per modelli, strumenti, agenti e
output strutturati. La documentazione include inoltre un'integrazione con
Ollama. Il flusso WLDT potrebbe quindi essere implementato con componenti del
framework.
Per questo progetto, tuttavia, l'uso di un agente generalista introdurrebbe un
livello di orchestrazione più ampio di quello strettamente necessario. Restano
comunque possibili utilizzi mirati di singoli componenti, per esempio per
l'integrazione con un modello o per la gestione dell'output strutturato.

## smolagents

smolagents fornisce classi per agenti multi-step e strumenti invocabili dal
modello. Anche questo approccio consentirebbe di esporre le operazioni WLDT
come tool e lasciare al modello la scelta di quale eseguire.
La prima versione del progetto, però, non richiede un ciclo autonomo in cui il
modello pianifica più azioni. La selezione delle operazioni, la validazione e
l'esecuzione devono restare esplicite e verificabili nel codice applicativo.

## Pipeline personalizzata

Il prototipo realizzato nel progetto separa il flusso nei seguenti componenti:

- selezione delle operazioni candidate;
- costruzione del prompt;
- invocazione di Ollama;
- parsing dell'output JSON;
- validazione;
- preparazione della richiesta REST.

Nell'Agent Service definitivo verranno aggiunti il caricamento dinamico
dell'OpenAPI, l'esecuzione HTTP e l'inoltro della risposta al client.
La pipeline personalizzata non introduce una capacità che LangChain o
smolagents non potrebbero offrire. La differenza riguarda il livello di
specializzazione: il flusso viene limitato alle sole operazioni necessarie al
dominio WLDT e ogni passaggio resta controllato dal servizio.

## Fonti

I riferimenti alla documentazione ufficiale consultata sono riportati in
`00_materiali/riferimenti.md`.

## Nota successiva all'implementazione — 12/08/2026

Le attività indicate nello studio come successive al prototipo sono state
realizzate nell'Agent Service definitivo.
In particolare sono stati aggiunti:

- caricamento dinamico della specifica OpenAPI;
- costruzione del catalogo delle operazioni;
- selezione deterministica delle candidate;
- structured output tramite Ollama;
- validazione rispetto alla OpenAPI corrente;
- preparazione ed esecuzione delle richieste HTTP;
- comunicazione con il Persistence Service reale;
- containerizzazione;
- integrazione nello stack WLDT development;
- integrazione nel Query Workbench;
- verifica end-to-end dal browser.

La scelta di mantenere una pipeline personalizzata non viene comunque
interpretata come dimostrazione di superiorità rispetto a LangChain o
smolagents.
E010 rimane uno studio documentale e progettuale e non costituisce un benchmark
prestazionale tra implementazioni equivalenti.
