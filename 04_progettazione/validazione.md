# Validazione della chiamata generata

## Obiettivo

Impedire l'esecuzione di chiamate inventate, incomplete o incompatibili con la
specifica esposta dal Persistence Service.

La validazione applicativa è separata dal vincolo JSON applicato durante la
generazione: un oggetto può rispettare lo schema generale dell'output e restare
comunque non valido rispetto a una specifica operazione REST.

## Livelli di controllo previsti

### 1. Parsing e struttura generale

- la risposta deve essere un singolo oggetto JSON;
- devono essere presenti `method`, `endpoint`, `pathParameters`,
  `queryParameters`, `body` e `missingInformation`;
- i campi devono avere i tipi previsti.

### 2. Coppia metodo/path

La combinazione deve corrispondere a un'operazione presente nella OpenAPI
corrente e, nella pipeline prevista, appartenere anche all'insieme delle
operazioni candidate.

### 3. Parametri

Per path e query vengono verificati:

- presenza dei parametri obbligatori;
- assenza di parametri non definiti;
- collocazione corretta;
- tipo e formato, quando ricavabili dalla specifica.

Il path prodotto dal modello resta un template; la sostituzione dei valori
avviene solo dopo la validazione.

### 4. Request body

Il body viene verificato rispetto allo schema associato all'operazione:

- presenza o assenza prevista;
- tipo radice, oggetto o array;
- campi obbligatori;
- tipi, enum e strutture annidate;
- eventuali riferimenti a schemi riutilizzabili.

### 5. Informazioni mancanti

Gli elementi in `missingInformation` devono corrispondere a dati realmente
obbligatori e non presenti né nella frase né nel contesto del client.

Campi obbligatori che ammettono valori vuoti validi non devono essere trattati
come informazioni mancanti. Per esempio, gli array di filtro della richiesta
`/query/event/stats` devono essere presenti ma possono essere vuoti.

### 6. Eseguibilità

Una chiamata è eseguibile soltanto quando:

- tutti i controlli precedenti sono superati;
- non rimangono informazioni obbligatorie mancanti;
- la specifica OpenAPI è disponibile e valida;
- l'URL di destinazione è quello configurato per il Persistence Service.

## Fonte della validazione

Catalogo delle operazioni e regole di validazione devono derivare dalla stessa
istanza della OpenAPI recuperata da `GET /openapi.yaml`. In questo modo un
aggiornamento della specifica non richiede la modifica manuale di due insiemi
di regole separati.

## Stato del prototipo

Il validatore presente in `05_codice/agent` copre soltanto:

- campi principali;
- appartenenza della coppia metodo/path ai candidati;
- placeholder del path;
- alcuni campi obbligatori codificati manualmente;
- coerenza di `missingInformation` per i casi coperti.

Non esegue ancora una validazione generale degli schemi OpenAPI. La versione
nell'Agent Service dovrà quindi sostituire le regole hard-coded con controlli
derivati dinamicamente dalla specifica.
