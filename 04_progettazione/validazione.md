# Validazione della chiamata generata

## Obiettivo

Una chiamata prodotta dal modello non viene eseguita direttamente.

Prima di raggiungere il Persistence Service deve superare una fase
deterministica di validazione rispetto alla specifica OpenAPI corrente.

La validazione deve impedire l'esecuzione di chiamate non conformi al contratto
e mantenere separata la generazione LLM dal controllo deterministico.

## Output strutturato

Ollama viene configurato per produrre una struttura compatibile con
`GeneratedApiCall`.

Il formato contiene:

```text
method
endpoint
pathParameters
queryParameters
body
missingInformation
```

Lo structured output riduce lo spazio delle risposte possibili, ma non
sostituisce la validazione OpenAPI.

## Operazione candidata

Il validatore verifica che:

```text
method + endpoint
```

corrispondano a una delle operazioni candidate fornite al modello.

Il path deve essere espresso nella forma dichiarata dalla OpenAPI.

Per esempio:

```text
/hdts/{id}/snapshot
```

e non:

```text
/hdts/HDT-001/snapshot
```

Il valore concreto deve essere mantenuto in `pathParameters`.

## Path parameter

Il validatore controlla:

- presenza dei parametri obbligatori;
- assenza di parametri non previsti;
- coerenza con i placeholder del path.

## Query parameter

Vengono controllati:

- parametri obbligatori;
- parametri forniti ma non previsti dall'operazione.

## Request body

Il body viene confrontato con lo schema OpenAPI.

I controlli comprendono, quando applicabili:

- presenza o assenza del body;
- tipo JSON atteso;
- oggetti;
- array;
- proprietà obbligatorie;
- proprietà non previste;
- tipi dei valori;
- enum;
- strutture annidate;
- riferimenti agli schemi OpenAPI.

Se l'operazione non prevede un request body, un body generato viene considerato
non valido.

Se la radice dello schema è un array, un singolo oggetto non viene accettato
come sostituto.

## Vincoli specifici delle operazioni

Alcune operazioni richiedono controlli aggiuntivi.

Per esempio:

```text
valuesByName
```

richiede l'utilizzo di:

```text
propertyName
```

mentre:

```text
valuesById
```

richiede:

```text
propertyId
```

## Informazioni mancanti

Prima dell'esecuzione viene controllato `missingInformation`.

Se contiene elementi, la pipeline restituisce HTTP 422 e non tenta alcuna
chiamata verso il Persistence Service.

## Chiamata non valida

Se il validatore rileva problemi, la pipeline restituisce HTTP 502.

La risposta include informazioni sull'errore e sulla chiamata generata, utili
alla diagnostica.

La chiamata non raggiunge il Persistence Service.

## Nessuna correzione automatica

Il validatore non modifica automaticamente la risposta del modello.

Se il modello genera una chiamata errata, questa viene rifiutata invece di
essere trasformata silenziosamente in una chiamata differente.

La scelta permette di mantenere indipendenti generazione e verifica.

## Validità OpenAPI e correttezza semantica

La validazione OpenAPI non equivale alla verifica completa dell'intenzione
dell'utente.

Nel benchmark finale il modello ha prodotto:

```text
GTE
```

per una richiesta:

```text
maggiore di 150
```

Il valore è valido secondo OpenAPI, ma non è semanticamente equivalente al
ground truth:

```text
GT
```

Per questo il benchmark misura separatamente:

```text
validation_valid
```

e:

```text
semantic_correct
```

## Sequenza

```text
LLM
 ↓
GeneratedApiCall
 ↓
missingInformation
 ↓
ApiCallValidator
 ↓
ApiRequestPreparer
 ↓
RestClient
 ↓
Persistence Service
```