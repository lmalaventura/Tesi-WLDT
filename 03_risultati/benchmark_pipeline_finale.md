# Benchmark controllato della pipeline implementata

Data di esecuzione: 10/08/2026
Risultato grezzo:

```text
02_esperimenti/pipeline_finale/results_20260810_201100.json
```

## Obiettivo

Valutare la pipeline completa dell'Agent Service dalla richiesta in linguaggio
naturale alla generazione della chiamata REST, alla validazione OpenAPI e
all'esecuzione verso un Persistence Service simulato.
Il benchmark utilizza cinque casi funzionali ripetuti tre volte ciascuno, per un
totale di 15 esecuzioni.

## Risultati complessivi

```text
Esecuzioni:                    15

Operazioni corrette:           12/15 = 80%
Argomenti corretti:             9/15 = 60%
Correttezza semantica:          9/15 = 60%
Validazioni OpenAPI superate:  12/15 = 80%
Esecuzioni Persistence:        12/15 = 80%
Successi end-to-end:            9/15 = 60%

Tempo medio complessivo:       25.731 s
```

## Risultati per caso

```text
Q1 — Elenco Digital Twin
Operation accuracy:   0%
Semantic accuracy:    0%
Validation pass:      0%
Execution success:    0%
End-to-end:           0%

Q2 — Snapshot corrente
Operation accuracy:   100%
Semantic accuracy:    100%
Validation pass:      100%
Execution success:    100%
End-to-end:           100%

Q3 — Storico in un intervallo
Operation accuracy:   100%
Semantic accuracy:    100%
Validation pass:      100%
Execution success:    100%
End-to-end:           100%

Q4 — Confronto
Operation accuracy:   100%
Semantic accuracy:    0%
Validation pass:      100%
Execution success:    100%
End-to-end:           0%

Q5 — Statistiche
Operation accuracy:   100%
Semantic accuracy:    100%
Validation pass:      100%
Execution success:    100%
End-to-end:           100%
```

## Q1 — Elenco Digital Twin

Q1 fallisce in tutte e tre le ripetizioni.
La richiesta richiede:

```text
GET /hdts
```

Il modello genera invece:

```text
POST /hdts
```

accompagnato da un request body di creazione contenente valori non presenti
nella richiesta dell'utente.
La chiamata generata non rispetta inoltre completamente lo schema OpenAPI
dell'operazione selezionata.
Il validatore intercetta l'errore e impedisce alla richiesta di raggiungere il
Persistence Service.
Questo caso mostra contemporaneamente:

- un errore della fase di generazione;
- l'efficacia del livello di validazione nel bloccare una richiesta non valida.

## Q2 — Snapshot corrente

Q2 è corretto in tutte e tre le ripetizioni.

La pipeline genera:

```text
GET /hdts/{id}/snapshot
```

e mantiene:

```text
id = HDT-001
```

separato nei `pathParameters`.
La richiesta supera la validazione ed è eseguita correttamente.

## Q3 — Valori di una proprietà in un intervallo

Q3 è corretto in tutte e tre le ripetizioni.
La pipeline utilizza:

```text
POST /query/event/values/valuesByName
```

con un body radice di tipo array.
Il modello utilizza correttamente:

```text
hdtId = HDT-001
propertyName = heartRate
from = 2026-07-01T00:00:00Z
to = 2026-07-08T00:00:00Z
```

La chiamata supera validazione ed esecuzione.

## Q4 — Confronto

Q4 seleziona correttamente metodo ed endpoint in tutte le ripetizioni:

```text
POST /query/event/comparison
```

Il modello traduce però:

```text
maggiore di 150
```

utilizzando:

```text
GTE
```

anziché il ground truth:

```text
GT
```

`GTE` è un valore valido secondo il contratto OpenAPI.
Per questo motivo la chiamata supera la validazione e viene eseguita dal
Persistence Service simulato.
La chiamata è tuttavia semanticamente diversa dalla richiesta naturale.
Questo caso evidenzia che:

```text
validità OpenAPI != correttezza semantica
```

La validazione strutturale può verificare che un operatore sia ammesso dalla
specifica, ma non garantisce da sola che rappresenti esattamente l'intento
espresso dall'utente.

## Q5 — Statistiche senza filtri

Q5 è corretto in tutte e tre le ripetizioni.
La pipeline genera:

```text
POST /query/event/stats
```

con:

```json
{
  "hdtIds": [],
  "modelIds": [],
  "modelNames": [],
  "propertyName": "heartRate",
  "from": "2026-07-01T00:00:00Z",
  "to": "2026-07-08T00:00:00Z"
}
```

La richiesta supera validazione ed esecuzione.

## Stabilità

L'esito funzionale dei cinque casi è stabile nelle tre ripetizioni.

```text
Q1: fallisce 3/3
Q2: corretto 3/3
Q3: corretto 3/3
Q4: stesso errore semantico 3/3
Q5: corretto 3/3
```

La configurazione a temperatura zero riduce la variabilità della generazione,
ma non elimina gli errori sistematici presenti nel comportamento del modello.

## Interpretazione

L'accuratezza dell'operazione raggiunge l'80%, mentre la correttezza semantica
end-to-end raggiunge il 60%.
La differenza mostra che individuare metodo ed endpoint corretti non è
sufficiente a garantire la correttezza della traduzione completa.
La validazione OpenAPI svolge comunque un ruolo importante nella pipeline.
Nel caso Q1 impedisce l'esecuzione di una richiesta non valida.
Q4 mostra invece il limite complementare: una chiamata può essere formalmente
valida e comunque non rappresentare esattamente l'intento dell'utente.

## Limiti metodologici

Il benchmark presenta alcuni limiti:

- comprende soltanto cinque tipologie funzionali;
- le tre ripetizioni non rappresentano quindici richieste indipendenti;
- i casi sono stati utilizzati anche durante sviluppo e diagnostica;
- il Persistence Service utilizzato è un mock;
- lo scoring semantico utilizza una ground truth esatta.

Il risultato deve quindi essere interpretato come benchmark controllato e
regressivo della pipeline e non come stima generale dell'accuratezza su
richieste arbitrarie.

## Congelamento del risultato

Il risultato del 10/08/2026 viene mantenuto senza modifiche retroattive.
Eventuali modifiche successive all'Agent Service e la futura valutazione su un
test set indipendente devono essere documentate in esperimenti separati, senza
sovrascrivere questo risultato.