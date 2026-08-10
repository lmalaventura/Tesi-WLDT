# Benchmark della pipeline finale

Data esecuzione: 10/08/2026

File risultati: `results_20260810_201100.json`

## Obiettivo

Valutare la pipeline completa dell'Agent Service dalla richiesta in linguaggio naturale alla generazione della chiamata REST, alla validazione OpenAPI e all'esecuzione verso un Persistence Service simulato.

Il benchmark usa 5 casi funzionali, ripetuti 3 volte ciascuno, per un totale di 15 esecuzioni.

## Metriche

- **Operation accuracy**: metodo HTTP ed endpoint coincidono con il ground truth.
- **Arguments accuracy**: path parameters, query parameters, body e `missingInformation` coincidono con il ground truth.
- **Semantic accuracy**: operazione e argomenti sono entrambi corretti.
- **Validation pass rate**: il validatore OpenAPI accetta la chiamata generata.
- **Execution success rate**: la chiamata raggiunge il Persistence Service simulato e riceve una risposta 2xx.
- **End-to-end success rate**: correttezza semantica, validazione ed esecuzione sono tutte soddisfatte.

## Risultati complessivi

| Metrica | Risultato |
|---|---:|
| Operazioni corrette | 12/15 (80.0%) |
| Argomenti corretti | 9/15 (60.0%) |
| Chiamate semanticamente corrette | 9/15 (60.0%) |
| Validazioni OpenAPI superate | 12/15 (80.0%) |
| Esecuzioni Persistence riuscite | 12/15 (80.0%) |
| Successi end-to-end | 9/15 (60.0%) |
| Tempo medio complessivo | 25.731 s |

## Risultati per caso

| Caso | Operazione | Semantica | Validazione | Esecuzione | End-to-end | Tempo medio |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 61.979 s |
| Q2 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 11.671 s |
| Q3 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 18.602 s |
| Q4 | 100.0% | 0.0% | 100.0% | 100.0% | 0.0% | 14.474 s |
| Q5 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 21.928 s |

## Analisi dei casi

### Q1 — Elenco Digital Twin

Il caso fallisce in tutte e tre le ripetizioni. La richiesta richiede `GET /hdts`, ma il modello genera `POST /hdts` con un body di creazione popolato con valori inventati. Il body non rispetta inoltre lo schema OpenAPI della relativa operazione. Il validatore intercetta l'errore e impedisce alla chiamata di raggiungere il Persistence Service.

Questo caso mostra due aspetti distinti: un errore di selezione/generazione dell'operazione e l'efficacia del livello di validazione nel bloccare una richiesta non conforme prima dell'esecuzione.

### Q2 — Snapshot corrente

Il caso è corretto in tutte le ripetizioni. La pipeline genera `GET /hdts/{id}/snapshot`, mantiene il placeholder OpenAPI nell'endpoint e inserisce `HDT-001` in `pathParameters`. La richiesta viene validata, preparata ed eseguita correttamente.

### Q3 — Valori di una proprietà in un intervallo

Il caso è corretto in tutte le ripetizioni. La pipeline seleziona `POST /query/event/values/valuesByName`, genera un body radice di tipo array e usa `propertyName = heartRate`, `hdtId = HDT-001` e i due estremi temporali attesi.

### Q4 — Confronto

Il metodo e l'endpoint sono corretti in tutte le ripetizioni, ma il modello traduce `maggiore di 150` come `GTE 150` invece di `GT 150`. La chiamata è formalmente valida secondo OpenAPI e viene quindi eseguita, ma non è semanticamente equivalente alla richiesta.

Il caso evidenzia che la validazione OpenAPI controlla la conformità strutturale e i valori ammessi dallo schema, ma non può da sola verificare la fedeltà semantica della traduzione rispetto alla frase originale.

### Q5 — Statistiche senza filtri su HDT o modello

Il caso è corretto in tutte le ripetizioni. La pipeline genera `POST /query/event/stats` e include gli array obbligatori `hdtIds`, `modelIds` e `modelNames` come array vuoti, oltre a `propertyName` e all'intervallo temporale atteso.

## Stabilità

L'esito funzionale è stabile nelle tre ripetizioni: Q2, Q3 e Q5 risultano sempre corretti; Q1 fallisce sempre nella scelta dell'operazione; Q4 usa sempre `GTE` al posto di `GT`. Nel body errato di Q1 sono presenti piccole variazioni di valori generati, ma non cambia la classe dell'errore.

## Tempi

Il tempo medio complessivo è 25.731 s. Q1 è il caso più lento (61.979 s medi), anche perché il modello produce un body molto più esteso di quello necessario. Tra i casi riusciti, i tempi medi vanno da 11.671 s per Q2 a 21.928 s per Q5.

## Interpretazione

Il benchmark mostra che il sistema gestisce correttamente tre delle cinque tipologie considerate in tutte le ripetizioni e seleziona il metodo/endpoint corretto in quattro tipologie su cinque. La differenza tra 80% di accuratezza dell'operazione e 60% di accuratezza semantica è significativa: selezionare l'endpoint corretto non garantisce che tutti gli argomenti esprimano esattamente l'intento dell'utente.

La validazione OpenAPI svolge un ruolo di sicurezza importante. Nel caso Q1 blocca una chiamata non conforme prima che raggiunga il backend. Q4 mostra invece il limite complementare: una chiamata può essere perfettamente valida per lo schema ma semanticamente sbagliata rispetto alla richiesta naturale.

## Limiti metodologici

- Il benchmark contiene solo 5 casi funzionali; le percentuali non vanno interpretate come una stima generale dell'accuratezza dell'agente su richieste arbitrarie.
- Le 3 ripetizioni misurano soprattutto la stabilità dei casi selezionati; non equivalgono a 15 richieste semanticamente indipendenti.
- I casi sono stati utilizzati anche durante lo sviluppo e la diagnostica della pipeline, quindi il benchmark è più correttamente interpretabile come benchmark controllato/regressivo che come test set completamente indipendente.
- L'esecuzione usa un Persistence Service simulato; il benchmark verifica la costruzione della richiesta e il percorso end-to-end dell'Agent Service, non il comportamento del Persistence Service reale o del database.
- Lo scoring semantico usa un ground truth esatto. In particolare, per Q5 assume la convenzione progettuale secondo cui array di filtro vuoti rappresentano l'assenza di restrizioni su HDT o modello.

## Stato del benchmark

Questi risultati costituiscono il risultato congelato del benchmark controllato della pipeline nella configurazione valutata il 10/08/2026. Eventuali modifiche successive all'agente devono essere documentate separatamente e non devono sovrascrivere questo risultato.
