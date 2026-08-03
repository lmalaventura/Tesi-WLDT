# Decisione progettuale

## Scelta

Per la prima versione dell'Agent Service viene mantenuta una pipeline
personalizzata in Python.

## Motivazione

Il flusso richiesto dal progetto è circoscritto e ordinato:

1. caricamento della specifica OpenAPI del Persistence Service;
2. selezione di operazioni candidate;
3. generazione di una chiamata strutturata tramite LLM;
4. validazione sulla stessa specifica;
5. esecuzione HTTP;
6. inoltro del risultato al client.

La pipeline rende questi passaggi espliciti e permette di testare
separatamente i componenti deterministici. La selezione preventiva delle API,
introdotta in seguito agli esperimenti E007 ed E008, è inoltre specifica del
problema studiato.

## Risposta alla domanda progettuale

La pipeline non svolge operazioni impossibili da realizzare con LangChain o
smolagents. Si distingue per l'attinenza ai requisiti del progetto:

- catalogo delle operazioni derivato dalla OpenAPI WLDT;
- contesto inviato al modello limitato alle operazioni candidate;
- nessuna esecuzione prima della validazione;
- assenza di un ciclo agentico autonomo non necessario;
- componenti ridotti e osservabili, pensati per un unico flusso applicativo.

Non viene rivendicato, nello stato attuale, un vantaggio di performance sui
framework esistenti. La scelta è motivata dalla riduzione dello scope e dal
controllo del comportamento. Se durante l'integrazione emergessero esigenze di
pianificazione multi-step, memoria o gestione dinamica di molti strumenti, la
decisione dovrà essere rivalutata.

## Stato

La scelta è stata ritenuta accettabile dal coordinatore, a condizione che sia
motivata e supportata dai test del progetto.
